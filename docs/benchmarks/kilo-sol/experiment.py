"""One Sol-solo / Sol+MiMo pair. prepare is offline; run spends on fixed arms."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = HERE.parent / 'adapter-batch'
V2 = BASE / 'selection-ablation'
KILO = Path.home() / '.codex/skills/kilo-delegator'
POINTER = HERE / 'local-fixture.json'
sys.path[:0] = [str(REPO / 'scripts'), str(BASE), str(V2)]
import deployment_runner as runner
from make_cases import build, FORMATS
from boundaries_visible import cases as visible_cases
from boundaries_hidden import cases as hidden_cases


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


kd = module('kilo_delegate', KILO / 'scripts/kilo_delegate.py')
read, save = runner.read_json, runner.atomic_json
sha = lambda p: kd.hashlib.sha256(Path(p).read_bytes()).hexdigest()


def call(argv, cwd, timeout=60):
    return subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True,
                          text=True, encoding='utf-8', timeout=timeout)


def grade(root, target, name):
    # Reuse the frozen grader, redirecting only its private fixture pointer.
    program = ("import importlib.util,sys; from pathlib import Path; "
               "s=importlib.util.spec_from_file_location('g',sys.argv[1]); "
               "g=importlib.util.module_from_spec(s); s.loader.exec_module(g); "
               "g.HERE=Path(sys.argv[2]); sys.argv=[sys.argv[1],sys.argv[3]]; raise SystemExit(g.main())")
    result = call([sys.executable, '-B', '-c', program, BASE / 'grade.py', root, target], target, 180)
    save(root / (name + '.json'), {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    return result.returncode


def config(disabled):
    values = {'model_provider': 'openai', 'model_reasoning_effort': 'high', 'approval_policy': 'never',
              'windows.sandbox': 'elevated', 'project_doc_max_bytes': 0, 'agents.enabled': False,
              'features.multi_agent': False, 'features.multi_agent_v2.enabled': False,
              'features.plugins': False, 'features.remote_plugin': False, 'features.memories': False,
              'memories.use_memories': False, 'memories.generate_memories': False, 'web_search': 'disabled'}
    args = []
    for key, value in values.items():
        args += ['-c', key + '=' + json.dumps(value)]
    return args + ['-c', 'mcp_servers={}', '-c', 'skills.config=[' + ','.join(
        '{path=' + json.dumps(p) + ',enabled=false}' for p in disabled) + ']']


def prepare():
    if POINTER.exists():
        raise ValueError('Pair already prepared; preserve existing evidence')
    # Python 3.13 mkdtemp uses a private Windows ACL inaccessible to Codex's
    # sandbox identity. A new ordinary directory inherits the host Temp ACL.
    root = Path(tempfile.gettempdir()) / ('kilo-sol-pair-' + uuid.uuid4().hex)
    root.mkdir()
    root = root.resolve()
    binary = shutil.which('codex.exe')
    assert binary and os.environ.get('CODEX_THREAD_ID'), 'Native CLI and current thread required'
    source = root / 'source'
    shutil.copytree(BASE / 'task', source, ignore=shutil.ignore_patterns('__pycache__'))
    save(source / 'fixtures.json', build())
    save(root / 'held-out.json', build(True) + hidden_cases())
    shutil.copy2(V2 / 'boundaries_visible.py', source / 'boundaries_visible.py')
    checker = source / 'check_contract.py'
    marker = "    cases = json.loads(cases_path.read_text(encoding='utf-8'))"
    text = checker.read_text(encoding='utf-8')
    assert text.count(marker) == 1
    checker.write_text(text.replace(marker, marker + "\n    if cases_path.name == 'fixtures.json':\n        from boundaries_visible import cases as boundary_cases\n        cases += boundary_cases()"), encoding='utf-8')
    with (source / 'TASK.md').open('a', encoding='utf-8') as stream:
        stream.write('\nThe checker also runs generated boundary cases from protected boundaries_visible.py.\n')
    owned = ['imports/adapters/' + fmt + '.py' for fmt in FORMATS]
    protected = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*') if p.is_file()
                 and p.relative_to(source).as_posix() not in owned}
    save(source / 'protected_hashes.json', protected)
    fixture = {'root': str(root), 'source': str(source), 'formats': list(FORMATS)}
    save(root / 'local-fixture.json', fixture)
    reference = root / 'reference'
    shutil.copytree(source, reference)
    for p in (BASE / 'reference').glob('*.py'):
        shutil.copy2(p, reference / 'imports/adapters' / p.name)
    shutil.copy2(V2 / 'reference_csv.py', reference / 'imports/adapters/_shared.py')
    for name in ('bank_csv.py', 'euro_csv.py'):
        p = reference / 'imports/adapters' / name
        p.write_text(p.read_text().replace('from .. import common', 'from .. import common\nfrom . import _shared')
                     .replace('reader = csv.reader(', 'reader = _shared.reader('), encoding='utf-8')
    assert grade(root, reference, 'qualification-reference') == 0
    assert grade(root, source, 'qualification-stubs') != 0
    mutant = root / 'legacy-csv-mutant'
    shutil.copytree(reference, mutant)
    for name in ('bank_csv.py', 'euro_csv.py'):
        p = mutant / 'imports/adapters' / name
        p.write_text(p.read_text().replace('reader = _shared.reader(', 'reader = csv.reader('), encoding='utf-8')
    assert grade(root, mutant, 'qualification-field-limit') != 0
    policy = root / 'policy'
    shutil.copytree(KILO, policy, ignore=shutil.ignore_patterns('__pycache__', '.git', 'tests'))
    disabled = sorted({str(p.resolve()).replace('\\', '/') for base in
                       (Path.home() / '.codex/skills', Path.home() / '.agents/skills') for p in base.rglob('SKILL.md')})
    cfg = config(disabled)
    for arm in ('solo', 'delegated'):
        task = root / arm / 'task'
        shutil.copytree(source, task)
        for argv in (['git', 'init', '-q'], ['git', 'add', '.'],
                     ['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@invalid', 'commit', '-qm', 'frozen input']):
            result = call(argv, task)
            assert result.returncode == 0, result.stderr
        job = {'provider': 'codex', 'profile': 'edit', 'cwd': str(task)}
        runner.preflight(binary, job, runner.worker_env('codex'))
    schema = {'type': 'object', 'additionalProperties': False, 'properties': {
        'mode': {'type': 'string', 'enum': ['implement']},
        **{key: {'type': 'string'} for key in ('objective', 'context')},
        **{key: {'type': 'array', 'items': {'type': 'string'}} for key in
           ('read_paths', 'write_paths', 'acceptance', 'constraints', 'judgment_calls')}}}
    schema['required'] = list(schema['properties'])
    save(root / 'contract-schema.json', schema)
    common = (f'Implement TASK.md completely. Use {sys.executable} -B -X utf8 for Python. '
              'Preserve protected files; write only the six adapter stubs, optional imports/adapters/_shared.py '
              'and optional test_adapters.py. Run the visible checker and added tests. '
              'Inspect your result against the contract, not just pass counts. Resolve material defects; '
              'report unsettled clauses as judgment calls rather than inventing requirements. '
              'No network, package installs, other agents, other repositories, personal context, previous solutions, '
              'reference files or external grading material. Do not inspect parent/sibling directories. '
              'Do not commit or leave background commands running. No unrelated hardening. ')
    solo = common + 'Do all implementation and verification yourself. End with a concise result and checks.'
    plan = (common.replace('No network, package installs, other agents,', 'No network, package installs, extra agents,') +
            f' This is preparation only, not implementation. Read the Kilo skill at {policy / "SKILL.md"} '
            'and its task-contract reference, plus TASK.md and only necessary starting evidence. '
            'Produce one bounded Kilo task contract as your JSON final response. Do not edit files or solve the adapters first. '
            'The host will run the wrapper with MiMo thinking, then resume this same Sol session for acceptance. '
            'Do not launch or poll anything yourself; the host handles the existing runtime procedure. '
            'Assign the entire adapter batch, development checks and corrections to that one worker. '
            'Set read_paths to ["TASK.md","imports","check_contract.py","fixtures.json","boundaries_visible.py","protected_hashes.json","test_adapters.py"]. '
            'Write_paths must name the six adapter files, optional imports/adapters/_shared.py and optional test_adapters.py only. '
            'External provider use on this synthetic fixture is authorized. No additional workers or external services.')
    (root / 'solo-prompt.txt').write_text(solo, encoding='utf-8')
    (root / 'plan-prompt.txt').write_text(plan, encoding='utf-8')
    (root / 'accept-prompt.txt').write_text(common +
        'The single Kilo attempt has terminated. Read KILO-RESULT.json and the actual complete candidate diff against HEAD, '
        'including new files, test evidence and judgment calls. Candidate files have been copied here without acceptance. '
        'You own verification and integration; make necessary corrections locally within this run, including completing '
        'partial work. Do not call another worker or reproduce already sufficient checks just for reporting. '
        'A failed or partial Kilo receipt is not an accepted result. Finish only after your review and required checks. '
        'End with acceptance status, checks, what you corrected and unresolved issues.', encoding='utf-8')
    # debug lacks exec's isolation flags; this only checks prompt discovery.
    # Paid stages separately use exec --ignore-user-config --ignore-rules.
    inspection = call([binary, 'debug', 'prompt-input', *cfg, solo], root / 'solo/task')
    save(root / 'prompt-preflight.json', {'exit_code': inspection.returncode, 'stdout': inspection.stdout, 'stderr': inspection.stderr})
    assert inspection.returncode == 0, inspection.stderr
    assert '### Available skills' not in inspection.stdout, 'Unexpected skill discovery'
    settings = read(KILO / 'settings.json')
    assert settings['model'] == 'kilo/xiaomi/mimo-v2.6-pro' and settings['variant'] == 'thinking'
    manifest = {**fixture, 'binary': binary, 'thread': os.environ['CODEX_THREAD_ID'], 'config': cfg,
                'order': ['solo', 'delegated'], 'model': 'gpt-5.6-sol', 'effort': 'high',
                'kilo_settings': settings, 'public_cases': len(build()) + len(visible_cases()),
                'held_out_cases': len(build(True) + hidden_cases()), 'automatic_retry': False,
                'owned': owned + ['imports/adapters/_shared.py', 'test_adapters.py'],
                'prepared_at': time.time(), 'sol_timeout_seconds': 1800, 'kilo_timeout_seconds': 1800}
    frozen_paths = [Path(__file__), BASE / 'grade.py', KILO / 'scripts/kilo_delegate.py', KILO / 'settings.json']
    frozen_paths += [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    manifest['frozen'] = {str(p): sha(p) for p in frozen_paths}
    save(root / 'manifest.json', manifest)
    save(POINTER, {'root': str(root)})
    save(root / 'notify-request.json', {'codex': binary, 'thread': manifest['thread'], 'cwd': str(REPO),
         'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run'], 'receipt': str(root / 'result.json')})
    print(json.dumps({'prepared': str(root), 'visible': manifest['public_cases'], 'held_out': manifest['held_out_cases'], 'paid_calls': 0}))


def jsonl_events(path):
    # JSONL is LF-framed; str.splitlines also splits valid U+2028 in strings.
    with Path(path).open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip().startswith('{')]


def sol(root, manifest, arm, label, prompt, tid=None, schema=None):
    folder, task = root / arm, root / arm / 'task'
    command = [manifest['binary'], 'exec', '--ignore-user-config', '--ignore-rules', '--strict-config',
               '--sandbox', 'workspace-write', '--cd', str(task), *manifest['config']]
    if tid:
        command += ['resume', tid]
    command += ['--json', '--model', manifest['model'], '--output-last-message', str(folder / (label + '-final.txt'))]
    if schema:
        command += ['--output-schema', str(schema)]
    command += ['-']
    prompt_path = folder / (label + '-prompt.txt')
    prompt_path.write_text(prompt, encoding='utf-8')
    result = runner.execute(command, str(task), str(prompt_path), folder / label,
                            manifest['sol_timeout_seconds'], runner.worker_env('codex'), lambda p: None)
    save(folder / (label + '-process.json'), result)
    if result.get('ownership_check_required'):
        raise RuntimeError('Sol ownership unresolved')
    events = jsonl_events(result['stdout_path'])
    found = next((e['thread_id'] for e in events if e.get('type') == 'thread.started'), tid)
    save(folder / (label + '-session.json'), {'thread_id': found, 'exit_code': result.get('exit_code')})
    if result.get('exit_code') != 0 or result.get('timed_out'):
        raise RuntimeError('Sol stage failed: ' + label)
    assert found, 'Missing Sol session identity'
    return found


def run(recovery=False):
    root = Path(read(POINTER)['root'])
    manifest = read(root / 'manifest.json')
    result_path = root / ('recovery-result.json' if recovery else 'result.json')
    result = {'started_at': time.time(), 'arms': {}, 'automatic_retry': False}
    if recovery:
        prior = read(root / 'result.json')
        assert prior['status'] == 'failed' and prior['active_arm'] == 'solo'
        assert prior['error'].startswith('JSONDecodeError:') and not prior['arms']
        assert not (root / 'delegated/plan-process.json').exists(), 'Delegated arm already attempted'
        proc = read(root / 'solo/solo-process.json')
        assert proc['exit_code'] == 0 and not proc['timed_out'] and not proc['ownership_check_required']
        # Preserve and verify the original executable; only its parser/recovery
        # plumbing changes. All prompts, settings and untouched inputs stay frozen.
        original = root / 'experiment-original.py'
        for p, digest in manifest['frozen'].items():
            path = Path(p)
            if path == Path(__file__).resolve():
                assert sha(original) == digest, 'Original harness mismatch'
            elif path not in {root / 'solo/task' / name for name in manifest['owned']}:
                assert sha(path) == digest, 'Frozen input changed: ' + p
        assert grade(root, root / 'solo/task', 'solo-recovered-grade') == 0
        tid = next(e['thread_id'] for e in jsonl_events(proc['stdout_path']) if e.get('type') == 'thread.started')
        result.update(recovered_from=str(root / 'result.json'), harness_sha256=sha(__file__))
        result['arms']['solo'] = {'thread_id': tid, 'grade_exit_code': 0, 'reused_without_model_rerun': True}
    else:
        assert all(sha(p) == digest for p, digest in manifest['frozen'].items()), 'Frozen input changed'
    with (root / ('recovery-started.json' if recovery else 'started.json')).open('x') as stream:
        json.dump({'started_at': time.time()}, stream)
    try:
        for arm in (['delegated'] if recovery else manifest['order']):
            result['active_arm'] = arm
            save(result_path, result)
            print(arm + ' started', flush=True)
            if arm == 'solo':
                tid = sol(root, manifest, arm, 'solo', (root / 'solo-prompt.txt').read_text())
            else:
                tid = sol(root, manifest, arm, 'plan', (root / 'plan-prompt.txt').read_text(), schema=root / 'contract-schema.json')
                task = root / arm / 'task'
                assert not kd.git(task, 'status', '--porcelain').strip(), 'Planning changed the input checkout'
                contract = kd.validate_contract(read(root / arm / 'plan-final.txt'))
                assert set(contract['write_paths']) <= set(manifest['owned']), 'Assignment widens write scope'
                assert set(contract['read_paths']) <= set(manifest['owned']) | {'TASK.md', 'imports', 'check_contract.py', 'fixtures.json', 'boundaries_visible.py', 'protected_hashes.json'}, 'Assignment widens reads'
                save(root / arm / 'task-contract.json', contract)
                args = argparse.Namespace(repo=str(task), task_file=str(root / arm / 'task-contract.json'),
                    model=None, variant=None, steps=None, timeout_seconds=manifest['kilo_timeout_seconds'],
                    candidate=None, base_ref=None, dry_run=True, notify_thread=None, notify_codex=None)
                prepared = kd.start(args)
                assert prepared['status'] == 'prepared', prepared
                run_dir = Path(prepared['run_dir'])
                result['kilo_run_dir'] = str(run_dir)
                save(result_path, result)
                km = read(run_dir / 'manifest.json')
                with Path(km['lock']).open('x') as stream:
                    stream.write(str(run_dir))
                # Foreground adapter supervisor: software blocks; no model wake-up loop.
                kd.execute(run_dir)
                receipt = read(run_dir / 'receipt.json')
                if receipt.get('ownership_check_required') or receipt.get('status') == 'termination_unconfirmed' or Path(km['lock']).exists():
                    raise RuntimeError('Kilo ownership unresolved')
                candidate = Path(km['worktree'])
                changes = kd.changed_files(candidate, km['base_commit'])
                assert all(p in manifest['owned'] for p in changes), 'Kilo changed out-of-scope files'
                for name in changes:
                    assert (candidate / name).is_file() and not (candidate / name).is_symlink(), 'Unexpected deletion or symlink'
                    shutil.copy2(candidate / name, task / name)
                save(task / 'KILO-RESULT.json', {'receipt': receipt, 'changed_files': changes,
                     'handoff': read(run_dir / 'handoff.json') if (run_dir / 'handoff.json').exists() else None})
                # Do not reveal external grading results to the acceptance model.
                grade(root, candidate, 'delegated-worker-grade')
                sol(root, manifest, arm, 'accept', (root / 'accept-prompt.txt').read_text(), tid=tid)
            result['arms'][arm] = {'thread_id': tid, 'grade_exit_code': grade(root, root / arm / 'task', arm + '-grade')}
            save(result_path, result)
        result['status'] = 'finished'
    except Exception as exc:
        result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        result['finished_at'] = time.time()
        save(result_path, result)
        print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'finished' else 1


def recover():
    return run(recovery=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'recover'])
    args = parser.parse_args()
    raise SystemExit(globals()[args.action]())
