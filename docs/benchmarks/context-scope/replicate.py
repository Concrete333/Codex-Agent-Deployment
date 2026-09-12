"""Fresh replication of the frozen packet experiment. prepare is free; run spends."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

import experiment as base

POINTER = base.HERE / 'local-replication.json'


def prepare():
    if POINTER.exists():
        raise ValueError('Replication already prepared; do not overwrite')
    old = Path(base.read(base.POINTER)['root'])
    previous = base.read(old / 'manifest.json')
    state = Path(previous['state'])
    if (state / 'active.json').exists():
        raise ValueError('Unresolved shared ownership')
    identity = 'context-r2-' + uuid.uuid4().hex[:8]
    root = Path.home() / 'AgentDeploymentBenchmarks' / identity
    root.mkdir(parents=True)
    corpus = root / 'corpus'
    shutil.copytree(old / 'corpus', corpus)
    # Use the frozen source, not today's project state or prior worker artifacts.
    for name, digest in base.read(corpus / 'corpus.sha256.json').items():
        assert base.hashes(corpus)[name] == digest
    runs = []
    for item in previous['runs']:
        label = item['task'] + '-' + item['arm']
        folder = root / label
        task = folder / 'task'
        shutil.copytree(corpus, task)
        old_job = base.read(item['request'])
        shutil.copy2(Path(old_job['cwd']) / 'TASK.md', task / 'TASK.md')
        subprocess.run(['git', 'init', '-q', str(task)], check=True)
        job = copy.deepcopy(old_job)
        job.update(id=identity + '-' + label.lower(), cwd=str(task))
        job['protected_files'] = [str(task / Path(p).name) for p in old_job['protected_files']]
        job['checks'][0]['argv'] = [str(task) if a == old_job['cwd'] else a
                                     for a in old_job['checks'][0]['argv']]
        job = base.runner.validate(job)
        base.runner.preflight(str(base.BINARY), job, base.runner.worker_env('codex'))
        base.save(folder / 'request.json', job)
        runs.append(dict(item, folder=str(folder), request=str(folder / 'request.json')))
    # Qualify the actual sandbox checker separately from the clean worker checkouts.
    for name in base.TASKS:
        gold = base.read(old / (name + '-gold.json'))
        base.save(root / (name + '-gold.json'), gold)
        qualification = root / ('qualify-' + name)
        shutil.copytree(corpus, qualification)
        base.save(qualification / 'inventory.json', gold['rows'])
        assert base.grade(qualification, gold)['accepted']
        p = subprocess.run(base.sandbox(qualification, [sys.executable, '-B',
            str(base.HERE / 'experiment.py'), 'grade', '--task', str(qualification),
            '--keys', json.dumps(base.TASKS[name])]), capture_output=True, text=True,
            encoding='utf-8', timeout=90)
        base.save(root / (name + '-preflight.json'), dict(exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
        assert p.returncode == 0, p.stderr
    frozen = {}
    for path in [Path(__file__), base.HERE / 'experiment.py',
                 base.REPO / 'scripts/deployment_runner.py', base.REPO / 'scripts/deployment_hash.py',
                 base.REPO / 'scripts/claude_worker.py', base.REPO / 'docs/benchmarks/revision-ab/summarize.py']:
        frozen[str(path)] = base.runner.hashlib.sha256(path.read_bytes()).hexdigest()
    for item in runs:
        for name, digest in base.hashes(Path(item['folder'])).items():
            frozen[str(Path(item['folder']) / name)] = digest
    manifest = dict(previous, root=str(root), runs=runs, frozen=frozen,
                    previous_root=str(old), identity=identity, preflight='all four shell cwd probes and both graders passed')
    base.save(root / 'manifest.json', manifest)
    base.save(POINTER, {'root': str(root)})
    print(json.dumps({'root': str(root), 'preflight': manifest['preflight'], 'paid_runs': 4}))


def run():
    root = Path(base.read(POINTER)['root'])
    manifest = base.read(root / 'manifest.json')
    for path, digest in manifest['frozen'].items():
        assert base.runner.hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    with (root / 'started.json').open('x') as stream:
        json.dump({'time': time.time(), 'sessions': 4}, stream)
    for item in manifest['runs']:
        job = base.read(item['request'])
        print(json.dumps({'stage': 'starting', 'task': item['task'], 'arm': item['arm']}), flush=True)
        result = base.runner.run(job, Path(manifest['state']), str(base.BINARY))
        base.save(Path(item['folder']) / 'result.json', result)
        print(json.dumps({'stage': 'finished', 'task': item['task'], 'arm': item['arm'], 'status': result['status']}), flush=True)
        # No successor after an infrastructure failure or uncertain ownership.
        if result['status'] == 'blocked' or result.get('ownership_check_required') or (Path(manifest['state']) / 'active.json').exists():
            break
    summarize()


def summarize():
    base.POINTER = POINTER
    base.summarize()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'run', 'summarize'])
    args = parser.parse_args()
    {'prepare': prepare, 'run': run, 'summarize': summarize}[args.operation]()
