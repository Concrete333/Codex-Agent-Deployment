"""Fresh inventory implementations, optional Astra acceptance; no model polling."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
POINTER = HERE / 'local-three-arm.json'
spec = importlib.util.spec_from_file_location('inventory_transport', HERE.parent / 'kilo-sol/experiment.py')
pair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pair)
spec = importlib.util.spec_from_file_location('inventory_reference', HERE / 'reference.py')
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
read, save, sha = pair.read, pair.save, pair.sha
ARTIFACTS = ['inventory/engine.py', 'inventory/ledger.py', 'inventory/api.py']
PROTECTED = ['SPEC.md', 'AGENTS.md', 'tests/test_public.py', 'inventory/projection.py', 'inventory/__init__.py']
READS = ['SPEC.md', 'AGENTS.md', 'inventory', 'tests']


def allowed(name):
    return name in ARTIFACTS or (name.startswith('tests/test_worker') and name.endswith('.py') and name.count('/') == 1)


def grade(root, target, label):
    proc = pair.call([sys.executable, '-B', '-X', 'utf8', HERE / 'coverage.py', target,
                      '--protected', root / 'protected.json'], target, 120)
    added = pair.call([sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'discover',
                      '-s', 'tests', '-p', 'test_worker*.py', '-q'], target, 120)
    absent = added.returncode == 5 and 'Ran 0 tests' in added.stderr
    value = {'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr,
             'added': {'exit_code': added.returncode, 'stdout': added.stdout, 'stderr': added.stderr},
             'passed': proc.returncode == 0 and (added.returncode == 0 or absent)}
    save(root / (label + '.json'), value)
    return value


def prepare():
    if POINTER.exists():
        prior = Path(read(POINTER)['root'])
        assert not (prior/'started.json').exists(), 'Preserve already launched experiment'
        save(prior/'superseded-preflight.json', {'reason': 'Reprepared before inference; retain original artifacts', 'time': time.time()})
    os.environ['KILO_EXPERIMENTAL_OUTPUT_TOKEN_MAX'] = '65536'
    old_root = Path(read(HERE / 'local-pipeline.json')['root'])
    old = read(old_root / 'manifest.json')
    for p in (HERE / 'task').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            assert sha(p) == old['frozen'][str(p)], 'Original task changed'
    assert sha(HERE / 'grade.py') == old['frozen'][str(HERE / 'grade.py')]
    root = Path(tempfile.gettempdir()) / ('inventory-three-' + uuid.uuid4().hex)
    root.mkdir()
    shutil.copytree(HERE / 'task', root / 'source', ignore=shutil.ignore_patterns('__pycache__'))
    save(root / 'protected.json', {p: sha(root / 'source' / p) for p in PROTECTED})
    variants = {'reference': {}, 'starter': None,
        'alias_reference': {'ledger.py': reference.LEDGER.replace('from .projection import project', 'from .projection import project as view').replace('return project(', 'return view(')},
        'preview_commit': {'ledger.py': reference.LEDGER.replace('if not dry_run:', 'if True:')},
        'partial_stock_commit': {'ledger.py': reference.LEDGER.replace('step(stock, holds, event)', 'step(stock, holds, event)\n            self.balances = stock')},
        'input_alias': {'ledger.py': reference.LEDGER.replace('(dict(event), dict(receipt))', '(event, dict(receipt))')},
        'receipt_alias': {'ledger.py': reference.LEDGER.replace('(dict(event), dict(receipt))', '(dict(event), receipt)')},
        'replay_reapplied': {'ledger.py': reference.LEDGER.replace('if identity in seen:', 'if False:')},
        'reserved_transfer': {'engine.py': reference.ENGINE.replace('stock.get(key, 0) - held < n', 'stock.get(key, 0) < n')},
        'release_consumes': {'engine.py': reference.ENGINE.replace("if kind == 'ship':", "if kind in ('ship', 'release'):")},
        'bool_quantity': {'engine.py': reference.ENGINE.replace("type(event['quantity']) is not int", "not isinstance(event['quantity'], int)")},
        'shallow_hold_staging': {'ledger.py': reference.LEDGER.replace('deepcopy((self.balances, self.holds, self.seen))', '(dict(self.balances), dict(self.holds), dict(self.seen))')}}
    qualification = {}
    for name, overrides in variants.items():
        target = root / 'qualification' / name
        shutil.copytree(root / 'source', target)
        if overrides is not None:
            codes = {'engine.py': reference.ENGINE, 'ledger.py': reference.LEDGER, 'api.py': reference.API}
            if name not in ('reference', 'alias_reference'):
                assert any(codes[k] != v for k, v in overrides.items())
            for file, code in (codes | overrides).items():
                (target / 'inventory' / file).write_text(code, encoding='utf-8')
        result = grade(root, target, 'qualification-' + name)
        assert result['passed'] == (name in ('reference', 'alias_reference')), (name, result)
        qualification[name] = result['passed']
    binary = pair.runner.executable('codex.exe')
    disabled = sorted({str(p.resolve()).replace('\\', '/') for base in
        (Path.home()/'.codex/skills', Path.home()/'.agents/skills') for p in base.rglob('SKILL.md')})
    cfg = pair.config(disabled)
    common = (f'Implement SPEC.md completely in this checkout using Python {sys.executable} -B -X utf8. '
        'Own the complete inventory event component and focused tests. Read SPEC.md, AGENTS.md and necessary source. '
        'Write only inventory/engine.py, inventory/ledger.py, inventory/api.py and optional tests/test_worker*.py. '
        'Preserve all other files. Implement and test in small increments; save useful edits before expanding the solution. '
        'Run public and added tests. Inspect your implementation against the contract and correct material defects before finishing. '
        'Do not add unrelated hardening. Report unsettled requirements rather than inventing them. '
        'No delegation, network, packages, commits, background jobs, personal context, sibling/parent directories, '
        'previous solutions or evaluator/reference material. Return the supplied result schema with actual checks and remaining risks.')
    contract = {'mode': 'implement', 'objective': common, 'context': 'SPEC.md is authoritative; inventory/projection.py and inventory/__init__.py are protected. '
        f'PowerShell on Windows. Test: {sys.executable} -B -X utf8 -m unittest discover -s tests -q.',
        'read_paths': READS, 'write_paths': ARTIFACTS + ['tests'],
        'acceptance': ['All SPEC.md behavior; public and added tests pass; protected files unchanged.'],
        'constraints': ['In tests/, write only test_worker*.py. Do not edit test_public.py. No extra workers or paid services.'],
        'judgment_calls': ['Report unresolved contract ambiguity; do not change acceptance criteria.']}
    pair.kd.validate_contract(contract)
    prior = Path(read(HERE.parent / 'kilo-sol/local-repeat.json')['root'])
    shutil.copy2(prior / 'solo/handoff-schema.json', root / 'handoff-schema.json')
    save(root / 'task-contract.json', contract)
    (root / 'implement-prompt.txt').write_text(json.dumps(contract), encoding='utf-8')
    for name in ('SKILL.md', 'references/delegation.md'):
        dest = root / 'policy' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path.home() / '.codex/skills/agent-deployment' / name, dest)
    acceptance = (f'Read {root / "policy/SKILL.md"} and references/delegation.md. '
        'You own final acceptance of this inventory implementation. Read SPEC.md, WORKER-RESULT.json, the complete '
        'candidate diff including new files, check evidence and judgment calls. Resolve material correctness problems '
        'against the contract; report unsettled clauses rather than inventing requirements. '
        'Use existing valid checks; add discriminating tests where a specific gap needs them. '
        'Correct necessary defects locally, including finishing partial work. No second worker or external service. '
        'Do not repeat sound implementation or add unrelated hardening. Preserve WORKER-RESULT.json and protected files. '
        + common + ' A failed worker is not an accepted implementation. Return the supplied result schema.')
    # Acceptance shares scope/testing constraints, without asking it to implement a second solution.
    acceptance = acceptance.replace(common, common[common.index('Write only'):common.index('Return the supplied')])
    (root / 'accept-prompt.txt').write_text(acceptance, encoding='utf-8')
    for kind in ('solo', 'luna', 'mimo'):
        for owner in (('delegated', 'worker') if kind == 'luna' else ('delegated',)):
            target = root / kind / owner / 'task'
            shutil.copytree(root / 'source', target)
            for args in (['git', 'init', '-q'], ['git', 'config', 'core.autocrlf', 'false'], ['git', 'add', '.'],
                ['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@invalid', 'commit', '-qm', 'frozen inventory input']):
                proc = pair.call(args, target)
                assert proc.returncode == 0, proc.stderr
            pair.runner.preflight(binary, {'provider': 'codex', 'profile': 'edit', 'cwd': str(target)}, pair.runner.worker_env('codex'))
    # Preflight the actual Kilo worktree before any paid stage.
    prepared = pair.kd.start(argparse.Namespace(repo=str(root/'mimo/delegated/task'), task_file=str(root/'task-contract.json'),
        model=None, variant=None, steps=0, timeout_seconds=1800, candidate=None, base_ref=None,
        dry_run=True, notify_thread=None, notify_codex=None))
    assert prepared['status'] == 'prepared', prepared
    km = read(Path(prepared['run_dir']) / 'manifest.json')
    assert km['model'] == 'kilo/xiaomi/mimo-v2.6-pro' and km['variant'] == 'thinking' and km['steps'] is None
    order = ['solo', 'luna', 'mimo']
    random.Random(20260922).shuffle(order)
    accounting = pair.module('inventory_rates', HERE.parent/'revision-ab/summarize.py')
    frozen = [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    frozen += [Path(__file__), HERE/'coverage.py', HERE/'grade.py', HERE/'reference.py', Path(pair.__file__),
        REPO/'scripts/deployment_runner.py', REPO/'scripts/claude_worker.py',
        pair.KILO/'scripts/kilo_delegate.py', pair.KILO/'settings.json', HERE.parent/'revision-ab/summarize.py']
    kr = Path(prepared['run_dir'])
    frozen += [kr/name for name in ('manifest.json', 'task.json', 'worker-config.json', 'resolved-agent.json')]
    manifest = {'root': str(root), 'binary': binary, 'config': cfg, 'model': 'gpt-6-astra', 'effort': 'high',
        'sol_timeout_seconds': 1800, 'qualification': qualification, 'kilo_run_dir': prepared['run_dir'],
        'order': order, 'launch_mode': 'concurrent independent arms', 'maximum_sessions': 5, 'automatic_retry': False,
        'thread': os.environ['CODEX_THREAD_ID'], 'rates_per_million': accounting.RATES, 'kilo_output_token_max': 65536,
        'codex_version': pair.call([binary, '--version'], root).stdout.strip(), 'kilo_version': km['kilo_version'],
        'frozen': {str(p.resolve()): sha(p) for p in frozen}}
    save(root / 'manifest.json', manifest)
    save(POINTER, {'root': str(root)})
    save(root/'notify-request.json', {'codex': binary, 'thread': manifest['thread'], 'cwd': str(REPO),
        'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run'], 'receipt': str(root/'result.json')})
    print(json.dumps({'prepared': str(root), 'methods': 27, 'qualification': qualification, 'paid_calls': 0}))


def run_arm(root, m, kind):
    arm, task = root/kind, root/kind/'delegated/task'
    result = {'status': 'running', 'sessions': {}, 'started_at': time.time(), 'automatic_retry': False}
    try:
        prompt = (root/'implement-prompt.txt').read_text(encoding='utf-8')
        if kind == 'solo':
            result['sessions']['astra'] = pair.sol(arm, m, 'delegated', 'implement', prompt, schema=root/'handoff-schema.json')
        else:
            if kind == 'luna':
                wm = {**m, 'model': m.get('luna_model', 'gpt-5.6-luna'), 'config': [v.replace('model_reasoning_effort="high"', 'model_reasoning_effort="max"') for v in m['config']]}
                try:
                    result['sessions']['luna'] = pair.sol(arm, wm, 'worker', 'implement', prompt, schema=root/'handoff-schema.json')
                except (RuntimeError, ValueError, AssertionError) as exc:
                    result['worker_error'] = str(exc)
                proc = read(arm/'worker/implement-process.json')
                assert not proc['ownership_check_required'] and proc['exit_code'] is not None
                session = read(arm/'worker/implement-session.json')
                result['sessions']['luna'] = session['thread_id']
                worker = arm/'worker/task'
                worker_receipt = {k: proc[k] for k in ('exit_code', 'timed_out', 'ownership_check_required', 'duration_seconds')}
                handoff_path = arm/'worker/implement-final.txt'
            else:
                kr = Path(m['kilo_run_dir'])
                km = read(kr/'manifest.json')
                with Path(km['lock']).open('x') as f:
                    f.write(str(kr))
                pair.kd.execute(kr)
                worker_receipt = read(kr/'receipt.json')
                assert not worker_receipt.get('ownership_check_required') and not worker_receipt.get('termination_unconfirmed')
                assert not Path(km['lock']).exists()
                worker, handoff_path = Path(km['worktree']), kr/'handoff.json'
                result['kilo_run_dir'] = str(kr)
            changes = pair.kd.changed_files(worker, pair.kd.git(worker, 'rev-parse', 'HEAD').strip())
            assert all(allowed(p) for p in changes), 'Out-of-scope worker change'
            for name in changes:
                assert (worker/name).is_file() and not (worker/name).is_symlink()
                shutil.copy2(worker/name, task/name)
            try:
                handoff = read(handoff_path)
            except (ValueError, OSError):
                handoff = None
            save(task/'WORKER-RESULT.json', {'receipt': worker_receipt, 'handoff': handoff, 'changed_files': changes})
            evidence_hash = sha(task/'WORKER-RESULT.json')
            result['worker_passed'] = grade(root, worker, kind+'-worker-grade')['passed']
            result['sessions']['astra'] = pair.sol(arm, m, 'delegated', 'accept',
                (root/'accept-prompt.txt').read_text(encoding='utf-8'), schema=root/'handoff-schema.json')
            assert sha(task/'WORKER-RESULT.json') == evidence_hash, 'Acceptance changed worker evidence'
        changes = pair.kd.changed_files(task, pair.kd.git(task, 'rev-parse', 'HEAD').strip())
        assert all(allowed(p) or (kind != 'solo' and p == 'WORKER-RESULT.json') for p in changes), 'Out-of-scope final change'
        result['final_passed'] = grade(root, task, kind+'-final-grade')['passed']
        final = read(arm/'delegated'/('implement-final.txt' if kind == 'solo' else 'accept-final.txt'))
        result['claimed_status'] = final.get('status')
        result['qualified'] = result['final_passed'] and final.get('status') == 'complete' and not final.get('blockers')
        result['status'] = 'finished'
    except Exception as exc:
        result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    result['finished_at'] = time.time()
    save(arm/'result.json', result)
    return result


def run():
    root = Path(read(POINTER)['root'])
    m = read(root/'manifest.json')
    assert all(sha(p) == h for p, h in m['frozen'].items()), 'Frozen input changed'
    os.environ['KILO_EXPERIMENTAL_OUTPUT_TOKEN_MAX'] = str(m['kilo_output_token_max'])
    with (root/'started.json').open('x') as f:
        json.dump({'started_at': time.time()}, f)
    result = {'status': 'running', 'arms': {}, 'maximum_sessions': 5}
    save(root/'result.json', result)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(run_arm, root, m, kind): kind for kind in m['order']}
        for future in as_completed(futures):
            kind = futures[future]
            result['arms'][kind] = future.result()
            save(root/'result.json', result)
    result['status'] = 'finished' if all(a['status'] == 'finished' for a in result['arms'].values()) else 'needs_attention'
    save(root/'result.json', result)
    print(json.dumps(result))
    return 0 if result['status'] == 'finished' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['prepare', 'run'])
    raise SystemExit(globals()[p.parse_args().action]())
