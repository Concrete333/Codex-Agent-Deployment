"""Offline recovery of fees-B gate; launch only the two not-yet-started funding cells."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from experiment import BINARY, HERE, POINTER, REPO, read, runner, save, summarize


def sandbox_hash(job, names):
    command = runner.build_check(str(BINARY), dict(job, profile='review'), {'argv': [sys.executable,
        '-I', '-B', str(REPO / 'scripts/deployment_hash.py')]})
    p = subprocess.run(command, cwd=job['cwd'], env=runner.worker_env('codex'),
                       input=json.dumps({'root': job['cwd'], 'names': names}),
                       capture_output=True, text=True, encoding='utf-8', timeout=60)
    if p.returncode:
        raise ValueError(p.stderr)
    value = json.loads(p.stdout)
    assert set(value) == set(names)
    return value


def recover(root, manifest):
    cell = next(c for c in manifest['runs'] if c['task'] == 'fees' and c['arm'] == 'B')
    job = read(cell['request'])
    state = Path(manifest['state'])
    receipt = read(state / job['id'] / 'receipt.json')
    assert receipt['status'] == 'blocked' and receipt['worker_process']['exit_code'] == 0
    for pid in [receipt['runner_pid'], *receipt['process_pids']]:
        assert not runner.pid_alive(pid), pid
    assert runner.protected_hashes(job) == receipt['protected_sha256']
    handoff = runner.validate_handoff(read(state / job['id'] / 'handoff.json'))
    assert handoff['status'] == 'complete'
    before = sandbox_hash(job, handoff['artifacts'])
    assert all(before[k] == v for k,v in receipt['artifact_sha256'].items())
    check = job['checks'][0]
    p = subprocess.run(runner.build_check(str(BINARY), job, check), cwd=job['cwd'],
                       env=runner.worker_env('codex'), capture_output=True, text=True,
                       encoding='utf-8', timeout=check['timeout_seconds'])
    assert sandbox_hash(job, handoff['artifacts']) == before
    assert runner.protected_hashes(job) == receipt['protected_sha256']
    result = {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr,
              'artifact_sha256': before, 'original_receipt_unchanged': True,
              'worker_retried': False, 'note': 'Offline evaluation, not an uninterrupted pipeline pass.'}
    save(Path(cell['folder']) / 'offline-grade.json', result)
    print(json.dumps(result), flush=True)
    assert p.returncode == 0
    if (state / 'active.json').exists():
        print(json.dumps(runner.release(state, job['id'], True)), flush=True)


def remaining(root, manifest):
    with (root / 'remaining-started.json').open('x') as stream:
        json.dump({'time': time.time(), 'new_model_calls': 2}, stream)
    for cell in manifest['runs']:
        if cell['task'] != 'funding':
            continue
        job = read(cell['request'])
        assert not (Path(manifest['state']) / job['id']).exists()
        print(json.dumps({'stage': 'starting', 'task': cell['task'], 'arm': cell['arm']}), flush=True)
        receipt = runner.run(job, Path(manifest['state']), str(BINARY))
        save(Path(cell['folder']) / 'result.json', receipt)
        print(json.dumps({'stage': 'finished', 'task': cell['task'], 'arm': cell['arm'], 'status': receipt['status']}), flush=True)
        if receipt.get('ownership_check_required') or (Path(manifest['state']) / 'active.json').exists():
            raise RuntimeError('Unresolved ownership; remaining cells not started')
    summarize()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['recover', 'remaining'])
    args = parser.parse_args()
    root = Path(read(POINTER)['root'])
    manifest = read(root / 'manifest.json')
    assert all(runner.hashlib.sha256(Path(p).read_bytes()).hexdigest() == sha for p,sha in manifest['frozen'].items())
    {'recover': recover, 'remaining': remaining}[args.operation](root, manifest)
