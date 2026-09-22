"""Reuse the frozen inventory trial for three explicitly selected Kilo workers."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import uuid

import three_arm as trial

HERE = Path(__file__).resolve().parent
POINTER = HERE / 'local-external-workers.json'
WORKERS = {
    'mimo': ('kilo/xiaomi/mimo-v2.6-pro', 'thinking'),
    'glm': ('kilo/z-ai/glm-5.3-flash', 'max'),
    'deepseek': ('kilo/deepseek/deepseek-v4.1-flash', 'max'),
}


def selected_catalog(text):
    result = {}
    for name, (model, variant) in WORKERS.items():
        match = re.search(r'^' + re.escape(model) + r'\r?\n', text, re.M)
        if not match:
            raise ValueError('Requested model unavailable: ' + model)
        metadata, _ = json.JSONDecoder().raw_decode(text[match.end():].lstrip())
        expected = {'enabled': True, 'effort': 'high' if name == 'mimo' else 'max'}
        if metadata.get('variants', {}).get(variant, {}).get('reasoning') != expected:
            raise ValueError('Reasoning configuration differs: ' + model)
        if metadata['limit']['output'] < 65536:
            raise ValueError('Output allowance below trial ceiling: ' + model)
        result[name] = metadata
    return result


def prepare():
    if POINTER.exists():
        raise ValueError('Existing preparation retained; inspect before creating another')
    prior = Path(trial.read(HERE / 'local-three-arm.json')['root'])
    old = trial.read(prior / 'manifest.json')
    root = Path(tempfile.gettempdir()) / ('inventory-external-' + uuid.uuid4().hex)
    root.mkdir()
    for name in ('source', 'policy'):
        shutil.copytree(prior/name, root/name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('protected.json', 'handoff-schema.json', 'task-contract.json', 'implement-prompt.txt'):
        shutil.copy2(prior/name, root/name)
    (root/'accept-prompt.txt').write_text(
        (prior/'accept-prompt.txt').read_text(encoding='utf-8').replace(str(prior), str(root)), encoding='utf-8')
    for p in (prior/'source').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            assert trial.sha(p) == old['frozen'][str(p.resolve())], 'Frozen starter changed'
    for name in ('coverage.py', 'grade.py', 'reference.py'):
        assert trial.sha(HERE/name) == old['frozen'][str((HERE/name).resolve())], 'Grader changed'
    qualification = {}
    for candidate, expected in old['qualification'].items():
        qualification[candidate] = trial.grade(root, prior/'qualification'/candidate,
                                                'qualification-' + candidate)['passed']
        assert qualification[candidate] == expected, candidate
    binary = trial.pair.kd.kilo_executable()
    catalog = trial.pair.call([binary, 'models', 'kilo', '--verbose'], root)
    assert catalog.returncode == 0, catalog.stderr
    metadata = selected_catalog(catalog.stdout)
    trial.save(root/'model-catalog.json', metadata)
    os.environ['KILO_EXPERIMENTAL_OUTPUT_TOKEN_MAX'] = '65536'
    runs = {}
    for name, (model, variant) in WORKERS.items():
        task = root/name/'delegated/task'
        shutil.copytree(root/'source', task)
        for args in (['git', 'init', '-q'], ['git', 'config', 'core.autocrlf', 'false'], ['git', 'add', '.'],
                     ['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@invalid',
                      'commit', '-qm', 'frozen inventory input']):
            proc = trial.pair.call(args, task)
            assert proc.returncode == 0, proc.stderr
        trial.pair.runner.preflight(old['binary'], {'provider': 'codex', 'profile': 'edit', 'cwd': str(task)},
                                    trial.pair.runner.worker_env('codex'))
        prepared = trial.pair.kd.start(argparse.Namespace(repo=str(task), task_file=str(root/'task-contract.json'),
            model=model, variant=variant, steps=0, timeout_seconds=1800, candidate=None, base_ref=None,
            dry_run=True, notify_thread=None, notify_codex=None))
        assert prepared['status'] == 'prepared', prepared
        run = Path(prepared['run_dir'])
        km = trial.read(run/'manifest.json')
        assert (km['model'], km['variant'], km['steps']) == (model, variant, None)
        runs[name] = str(run)
    frozen = [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    frozen += [Path(__file__), HERE/'three_arm.py', HERE/'coverage.py', HERE/'grade.py', HERE/'reference.py',
               Path(trial.pair.__file__), trial.pair.KILO/'scripts/kilo_delegate.py', trial.pair.KILO/'settings.json',
               trial.REPO/'scripts/deployment_runner.py', trial.REPO/'scripts/claude_worker.py']
    for run in runs.values():
        frozen += [Path(run)/p for p in ('manifest.json', 'task.json', 'worker-config.json', 'resolved-agent.json')]
    manifest = {k: old[k] for k in ('binary', 'config', 'model', 'effort', 'sol_timeout_seconds', 'rates_per_million')}
    manifest.update(root=str(root), prior_root=str(prior), thread=os.environ['CODEX_THREAD_ID'],
        workers=runs, requested_models=WORKERS, maximum_sessions=6, automatic_retry=False,
        qualification=qualification, kilo_output_token_max=65536,
        codex_version=trial.pair.call([old['binary'], '--version'], root).stdout.strip(),
        kilo_version=trial.pair.call([binary, '--version'], root).stdout.strip(),
        frozen={str(p.resolve()): trial.sha(p) for p in frozen})
    trial.save(root/'manifest.json', manifest)
    trial.save(POINTER, {'root': str(root)})
    trial.save(root/'notify-request.json', {'codex': old['binary'], 'thread': manifest['thread'],
        'cwd': str(trial.REPO), 'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run', '--root', str(root)],
        'receipt': str(root/'result.json')})
    print(json.dumps({'prepared': str(root), 'workers': runs, 'qualification': qualification, 'paid_calls': 0}))


def run(root):
    m = trial.read(root/'manifest.json')
    assert all(trial.sha(p) == h for p, h in m['frozen'].items()), 'Frozen input changed'
    os.environ['KILO_EXPERIMENTAL_OUTPUT_TOKEN_MAX'] = str(m['kilo_output_token_max'])
    with (root/'started.json').open('x') as stream:
        json.dump({'started_at': time.time()}, stream)
    result = {'status': 'running', 'arms': {}, 'maximum_sessions': 6, 'automatic_retry': False}
    trial.save(root/'result.json', result)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(trial.run_arm, root, {**m, 'kilo_run_dir': run}, name): name
                   for name, run in m['workers'].items()}
        for future in as_completed(futures):
            result['arms'][futures[future]] = future.result()
            trial.save(root/'result.json', result)
    result['status'] = 'finished' if all(a['status'] == 'finished' for a in result['arms'].values()) else 'needs_attention'
    trial.save(root/'result.json', result)
    print(json.dumps(result))
    return 0 if result['status'] == 'finished' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run'])
    parser.add_argument('--root', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    else:
        if args.root is None:
            parser.error('run requires --root')
        raise SystemExit(run(args.root))
