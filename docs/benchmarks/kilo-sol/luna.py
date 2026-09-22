"""One Sol High -> Luna Max -> resumed Sol High arm on the frozen pair task."""
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
POINTER = HERE / 'local-luna.json'
read, save = pair.read, pair.save
POLICY = Path.home() / '.codex/skills/agent-deployment'


def prepare():
    assert not POINTER.exists(), 'Preserve existing trial'
    previous = Path(read(pair.POINTER)['root'])
    original = read(previous / 'manifest.json')
    root = Path(tempfile.gettempdir()) / ('sol-luna-' + uuid.uuid4().hex)
    root.mkdir()
    for path in (previous / 'source').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            assert pair.sha(path) == original['frozen'][str(path)], 'Original source changed'
    shutil.copytree(previous / 'source', root / 'source', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(previous / 'held-out.json', root / 'held-out.json')
    assert pair.sha(root / 'held-out.json') == original['frozen'][str(previous / 'held-out.json')]
    save(root / 'local-fixture.json', {'root': str(root), 'source': str(root / 'source'), 'formats': original['formats']})
    for arm in ('delegated', 'worker'):
        task = root / arm / 'task'
        shutil.copytree(root / 'source', task)
        for argv in (['git', 'init', '-q'], ['git', 'config', 'core.autocrlf', 'false'],
                     ['git', 'add', '.'], ['git', '-c', 'user.name=Benchmark', '-c',
                      'user.email=benchmark@invalid', 'commit', '-qm', 'frozen input']):
            p = pair.call(argv, task)
            assert p.returncode == 0, p.stderr
        pair.runner.preflight(original['binary'], {'provider': 'codex', 'profile': 'edit', 'cwd': str(task)},
                              pair.runner.worker_env('codex'))
    for name in ('SKILL.md', 'references/delegation.md', 'references/waiting.md'):
        dest = root / 'policy' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(POLICY / name, dest)
    shutil.copy2(previous / 'contract-schema.json', root / 'contract-schema.json')
    schema = {'type': 'object', 'additionalProperties': False, 'properties': {
        'status': {'type': 'string', 'enum': ['complete', 'partial', 'blocked']},
        'summary': {'type': 'string'},
        **{k: {'type': 'array', 'items': {'type': 'string'}} for k in
           ('files_changed', 'checks', 'judgment_calls', 'blockers')}}}
    schema['required'] = list(schema['properties'])
    save(root / 'handoff-schema.json', schema)
    plan = (previous / 'plan-prompt.txt').read_text(encoding='utf-8')
    plan = plan.replace('Read the Kilo skill at ' + str(previous / 'policy/SKILL.md') +
                        ' and its task-contract reference',
                        'Read the deployment skill at ' + str(root / 'policy/SKILL.md') +
                        ' and its references/delegation.md guidance')
    plan = plan.replace('bounded Kilo task contract', 'bounded Luna task contract').replace(
        'the wrapper with MiMo thinking', 'a Codex CLI worker with Luna Max')
    plan = plan.replace('External provider use on this synthetic fixture is authorized.',
                        'This single Luna Max worker on the synthetic fixture is authorized.')
    assert 'Kilo' not in plan and 'MiMo' not in plan
    (root / 'plan-prompt.txt').write_text(plan, encoding='utf-8')
    acceptance = (previous / 'accept-prompt.txt').read_text(encoding='utf-8').replace('KILO-RESULT', 'WORKER-RESULT').replace('Kilo', 'Luna')
    (root / 'accept-prompt.txt').write_text(acceptance, encoding='utf-8')
    # Same checker/reference, no new counterexample or previous solution supplied.
    assert pair.grade(root, previous / 'reference', 'qualification-reference') == 0
    assert pair.grade(root, root / 'source', 'qualification-stubs') != 0
    manifest = {k: original[k] for k in ('binary', 'config', 'model', 'effort', 'owned',
                'sol_timeout_seconds', 'public_cases', 'held_out_cases')}
    manifest.update(root=str(root), previous=str(previous), thread=os.environ['CODEX_THREAD_ID'],
                    worker_model='gpt-5.6-luna', worker_effort='max', worker_timeout_seconds=1800,
                    prepared_at=time.time(), automatic_retry=False)
    frozen = [Path(__file__), Path(pair.__file__), pair.BASE / 'grade.py',
              pair.REPO / 'scripts/deployment_runner.py', pair.REPO / 'scripts/claude_worker.py']
    frozen += [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    manifest['frozen'] = {str(p.resolve()): pair.sha(p) for p in frozen}
    save(root / 'manifest.json', manifest)
    save(POINTER, {'root': str(root)})
    save(root / 'notify-request.json', {'codex': manifest['binary'], 'thread': manifest['thread'],
        'cwd': str(pair.REPO), 'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run'],
        'receipt': str(root / 'result.json')})
    print(json.dumps({'prepared': str(root), 'paid_calls': 0, 'cases': [146, 98]}))


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
        tid = pair.sol(root, m, 'delegated', 'plan', (root / 'plan-prompt.txt').read_text(),
                       schema=root / 'contract-schema.json')
        result['sessions']['sol'] = tid
        task, worker = root / 'delegated/task', root / 'worker/task'
        assert not pair.kd.git(task, 'status', '--porcelain').strip(), 'Preparation edited checkout'
        contract = pair.kd.validate_contract(read(root / 'delegated/plan-final.txt'))
        assert set(contract['write_paths']) <= set(m['owned'])
        assert set(contract['read_paths']) <= set(m['owned']) | {'TASK.md', 'imports', 'check_contract.py',
               'fixtures.json', 'boundaries_visible.py', 'protected_hashes.json'}
        save(root / 'task-contract.json', contract)
        worker_config = [v.replace('model_reasoning_effort="high"', 'model_reasoning_effort="max"')
                         for v in m['config']]
        wm = {**m, 'model': m['worker_model'], 'config': worker_config,
              'sol_timeout_seconds': m['worker_timeout_seconds']}
        prompt = ('Implement the following assignment in this checkout. Read TASK.md and the necessary source. '
                  'Do not delegate, inspect parent/sibling directories, access previous solutions, use network, '
                  'install packages, commit, or leave background processes. Own implementation, tests and '
                  'corrections within the contract. Return complete, partial or blocked with exact changed '
                  'paths, checks, judgment calls and blockers. A handoff is not acceptance.\n' + json.dumps(contract))
        result['stage'] = 'worker'
        save(root / 'result.json', result)
        try:
            result['sessions']['luna'] = pair.sol(root, wm, 'worker', 'worker', prompt,
                                                 schema=root / 'handoff-schema.json')
        except (RuntimeError, ValueError, AssertionError) as exc:
            # A terminated failed attempt can still contain useful work; review
            # locally as in the MiMo arm, but never hand off uncertain ownership.
            result['worker_error'] = str(exc)
        proc = read(root / 'worker/worker-process.json')
        assert not proc['ownership_check_required'] and proc['exit_code'] is not None
        if (root / 'worker/worker-session.json').exists():
            result['sessions']['luna'] = read(root / 'worker/worker-session.json')['thread_id']
        changes = pair.kd.changed_files(worker, pair.kd.git(worker, 'rev-parse', 'HEAD').strip())
        assert set(changes) <= set(m['owned']), 'Out-of-scope worker changes'
        for name in changes:
            assert (worker / name).is_file() and not (worker / name).is_symlink()
            shutil.copy2(worker / name, task / name)
        handoff = None
        try:
            handoff = read(root / 'worker/worker-final.txt')
        except (ValueError, OSError) as exc:
            result['handoff_error'] = str(exc)
        save(task / 'WORKER-RESULT.json', {'receipt': {k: proc[k] for k in
             ('exit_code', 'timed_out', 'ownership_check_required', 'duration_seconds')},
             'handoff': handoff, 'changed_files': changes})
        result['worker_grade_exit_code'] = pair.grade(root, worker, 'worker-grade')
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
