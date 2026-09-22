"""Fresh Sol/MiMo/Sol arm without an iteration cap; reuse the frozen task."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import uuid

import experiment as pair

HERE = Path(__file__).resolve().parent
POINTER = HERE / 'local-uncapped.json'
read, save = pair.read, pair.save


def prepare():
    assert not POINTER.exists(), 'Preserve existing trial'
    previous = Path(read(pair.POINTER)['root'])
    old = read(previous / 'manifest.json')
    root = Path(tempfile.gettempdir()) / ('sol-mimo-uncapped-' + uuid.uuid4().hex)
    root.mkdir()
    for p in (previous / 'source').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            assert pair.sha(p) == old['frozen'][str(p)]
    shutil.copytree(previous / 'source', root / 'source', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(previous / 'held-out.json', root / 'held-out.json')
    assert pair.sha(root / 'held-out.json') == old['frozen'][str(previous / 'held-out.json')]
    save(root / 'local-fixture.json', {'root': str(root), 'source': str(root / 'source'), 'formats': old['formats']})
    task = root / 'delegated/task'
    shutil.copytree(root / 'source', task)
    for argv in (['git', 'init', '-q'], ['git', 'config', 'core.autocrlf', 'false'], ['git', 'add', '.'],
                 ['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@invalid', 'commit', '-qm', 'frozen input']):
        result = pair.call(argv, task)
        assert result.returncode == 0, result.stderr
    pair.runner.preflight(old['binary'], {'provider': 'codex', 'profile': 'edit', 'cwd': str(task)}, pair.runner.worker_env('codex'))
    shutil.copytree(pair.KILO, root / 'policy', ignore=shutil.ignore_patterns('__pycache__', '.git', 'tests'))
    shutil.copy2(previous / 'contract-schema.json', root / 'contract-schema.json')
    plan = (previous / 'plan-prompt.txt').read_text(encoding='utf-8').replace(str(previous / 'policy'), str(root / 'policy'))
    (root / 'plan-prompt.txt').write_text(plan, encoding='utf-8')
    shutil.copy2(previous / 'accept-prompt.txt', root / 'accept-prompt.txt')
    # Same acceptance response shape as the newly launched Luna arm.
    luna_root = Path(read(HERE / 'local-luna.json')['root'])
    shutil.copy2(luna_root / 'handoff-schema.json', root / 'handoff-schema.json')
    assert pair.grade(root, previous / 'reference', 'qualification-reference') == 0
    assert pair.grade(root, root / 'source', 'qualification-stubs') != 0
    settings = read(pair.KILO / 'settings.json')
    assert settings['steps'] is None and settings['model'] == 'kilo/xiaomi/mimo-v2.6-pro'
    m = {k: old[k] for k in ('binary', 'config', 'model', 'effort', 'owned', 'sol_timeout_seconds')}
    m.update(root=str(root), previous=str(previous), thread=os.environ['CODEX_THREAD_ID'],
             kilo_settings=settings, worker_timeout_seconds=1800, prepared_at=time.time())
    frozen = [Path(__file__), Path(pair.__file__), pair.BASE / 'grade.py',
              pair.REPO / 'scripts/deployment_runner.py', pair.REPO / 'scripts/claude_worker.py',
              pair.KILO / 'scripts/kilo_delegate.py', pair.KILO / 'settings.json']
    frozen += [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    m['frozen'] = {str(p.resolve()): pair.sha(p) for p in frozen}
    save(root / 'manifest.json', m)
    save(POINTER, {'root': str(root)})
    save(root / 'notify-request.json', {'codex': m['binary'], 'thread': m['thread'], 'cwd': str(pair.REPO),
         'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run'], 'receipt': str(root / 'result.json')})
    print(json.dumps({'prepared': str(root), 'steps': None, 'worker_timeout_seconds': 1800, 'paid_calls': 0}))


def run():
    root = Path(read(POINTER)['root'])
    m = read(root / 'manifest.json')
    assert all(pair.sha(p) == h for p, h in m['frozen'].items()), 'Frozen input changed'
    with (root / 'started.json').open('x') as f:
        json.dump({'started_at': time.time()}, f)
    result = {'started_at': time.time(), 'sessions': {}, 'automatic_retry': False}
    try:
        result['stage'] = 'plan'
        save(root / 'result.json', result)
        tid = pair.sol(root, m, 'delegated', 'plan', (root / 'plan-prompt.txt').read_text(), schema=root / 'contract-schema.json')
        result['sessions']['sol'] = tid
        task = root / 'delegated/task'
        assert not pair.kd.git(task, 'status', '--porcelain').strip(), 'Preparation edited checkout'
        contract = pair.kd.validate_contract(read(root / 'delegated/plan-final.txt'))
        assert set(contract['write_paths']) <= set(m['owned'])
        assert set(contract['read_paths']) <= set(m['owned']) | {'TASK.md', 'imports', 'check_contract.py',
               'fixtures.json', 'boundaries_visible.py', 'protected_hashes.json'}
        save(root / 'task-contract.json', contract)
        args = argparse.Namespace(repo=str(task), task_file=str(root / 'task-contract.json'), model=None,
            variant=None, steps=0, timeout_seconds=m['worker_timeout_seconds'], candidate=None,
            base_ref=None, dry_run=True, notify_thread=None, notify_codex=None)
        prepared = pair.kd.start(args)
        assert prepared['status'] == 'prepared', prepared
        run_dir = Path(prepared['run_dir'])
        km = read(run_dir / 'manifest.json')
        assert km['steps'] is None, 'Uncapped worker required'
        result.update(stage='worker', kilo_run_dir=str(run_dir))
        save(root / 'result.json', result)
        with Path(km['lock']).open('x') as f:
            f.write(str(run_dir))
        pair.kd.execute(run_dir)
        receipt = read(run_dir / 'receipt.json')
        assert not receipt.get('ownership_check_required') and not receipt.get('termination_unconfirmed')
        assert not Path(km['lock']).exists(), 'Worker ownership unresolved'
        candidate = Path(km['worktree'])
        changes = pair.kd.changed_files(candidate, km['base_commit'])
        assert set(changes) <= set(m['owned']), 'Out-of-scope worker changes'
        for name in changes:
            assert (candidate / name).is_file() and not (candidate / name).is_symlink()
            shutil.copy2(candidate / name, task / name)
        save(task / 'KILO-RESULT.json', {'receipt': receipt, 'changed_files': changes,
             'handoff': read(run_dir / 'handoff.json') if (run_dir / 'handoff.json').exists() else None})
        result['worker_grade_exit_code'] = pair.grade(root, candidate, 'worker-grade')
        result['stage'] = 'accept'
        save(root / 'result.json', result)
        pair.sol(root, m, 'delegated', 'accept', (root / 'accept-prompt.txt').read_text(),
                 tid=tid, schema=root / 'handoff-schema.json')
        result['grade_exit_code'] = pair.grade(root, task, 'delegated-grade')
        result['status'] = 'finished'
    except Exception as exc:
        result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        result['finished_at'] = time.time()
        save(root / 'result.json', result)
        print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'finished' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run'])
    args = parser.parse_args()
    raise SystemExit(globals()[args.action]())
