"""Frozen native/host-bridge pair. prepare is offline; run spends on two workflows."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SUITE = HERE.parent / 'adapter-batch/selection-ablation'
sys.path.insert(0, str(REPO / 'scripts'))
import deployment_runner as runner

BINARY = Path.home() / 'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
POINTER = HERE / 'local-fixture.json'
save = runner.atomic_json


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sandbox(task, argv):
    return [str(BINARY), 'sandbox', '-P', ':read-only', '-C', str(task),
            '-c', 'windows.sandbox="elevated"', '--', *map(str, argv)]


def observed(argv, folder, label, cwd=None, timeout=180):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    receipt = {'argv': argv, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    save(folder / (label + '.json'), receipt)
    return receipt


def overrides(native, disabled):
    config = {'model_provider': 'openai', 'model_reasoning_effort': 'high', 'approval_policy': 'never',
              'windows.sandbox': 'elevated', 'project_doc_max_bytes': 0,
              'features.memories': False, 'features.plugins': False, 'features.remote_plugin': False,
              'memories.use_memories': False, 'memories.generate_memories': False,
              'agents.enabled': native, 'agents.max_concurrent_threads_per_session': 1,
              'features.multi_agent': native, 'features.multi_agent_v2.enabled': native,
              'features.multi_agent_v2.min_wait_timeout_ms': 1500000,
              'features.multi_agent_v2.default_wait_timeout_ms': 1500000,
              'features.multi_agent_v2.max_wait_timeout_ms': 1500000, 'web_search': 'disabled'}
    args = []
    for key, value in config.items():
        args += ['-c', key + '=' + json.dumps(value)]
    args += ['-c', 'mcp_servers={}', '-c', 'skills.config=[' + ','.join(
        '{path=' + json.dumps(path) + ',enabled=false}' for path in disabled) + ']']
    return args


def tracked_files(fixture):
    source = read(SUITE / 'local-fixture.json')
    paths = [Path(__file__), SUITE / 'local-fixture.json', SUITE / 'grade.py', SUITE.parent / 'grade.py',
             HERE.parent / 'revision-ab/summarize.py', Path(source['root']) / 'held-out.json']
    for directory in (Path(source['source']), Path(source['reference']), Path(fixture['root']) / 'policy'):
        paths.extend(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for arm in ('native', 'software'):
        folder = Path(fixture['root']) / arm
        paths.extend(folder / name for name in ('prompt.txt', 'command.json', 'worker-request.json'))
    return {str(path): sha(path) for path in paths}


def prepare():
    if POINTER.exists():
        raise ValueError('Preserve existing comparison; no implicit rerun')
    source = read(SUITE / 'local-fixture.json')
    root = Path(tempfile.mkdtemp(prefix='agent-deployment-runner-pair-')).resolve()
    state = (Path(os.environ['LOCALAPPDATA']) / 'AgentDeployment' / root.name).resolve()
    policy = root / 'policy'
    policy.mkdir()
    shutil.copy2(REPO / 'SKILL.md', policy / 'SKILL.md')
    for name in ('references', 'scripts'):
        shutil.copytree(REPO / name, policy / name, ignore=shutil.ignore_patterns('__pycache__'))
    disabled = sorted({str(p.resolve()).replace('\\', '/') for base in
                       (Path.home() / '.codex/skills', Path.home() / '.agents/skills')
                       for p in base.rglob('SKILL.md')})
    fixture = {'root': str(root), 'state': str(state), 'policy': str(policy), 'source_fixture': source,
               'order': ['native', 'software'], 'timeout_seconds': 1200, 'worker_timeout_seconds': 900,
               'automatic_retry': False, 'prepared_at': time.time()}
    # Requalify the same grader on its reference and unimplemented starting point.
    for label, target, success in (('reference', source['reference'], True), ('stubs', source['source'], False)):
        result = observed(sandbox(target, [sys.executable, '-B', '-X', 'utf8', str(SUITE / 'grade.py'), target]), root, label)
        assert (result['exit_code'] == 0) == success, label
    owned = ['imports/adapters/' + fmt + '.py' for fmt in source['formats']]
    for arm in fixture['order']:
        folder = root / arm
        folder.mkdir()
        task = folder / 'task'
        shutil.copytree(source['source'], task, ignore=shutil.ignore_patterns('__pycache__', '.git'))
        subprocess.run(['git', 'init', '-q', str(task)], check=True)
        subprocess.run(['git', '-C', str(task), 'add', '.'], check=True)
        check = [sys.executable, '-B', '-X', 'utf8', 'check_contract.py']
        protected = list(read(task / 'protected_hashes.json')) + ['protected_hashes.json']
        assignment = (f'Work only in {task}. Read TASK.md and implement the complete six-adapter batch. '
                      f'Use {sys.executable} with -B -X utf8 for Python commands. '
                      'Own only the six stub modules, optional imports/adapters/_shared.py and optional test_*.py files. '
                      'Use existing helpers. Do local development checks and corrections within one attempt. '
                      'Do not inspect personal context, policies, external graders, reference solutions, other trials or repositories. '
                      'No network, dependency installs, delegation, background work or unrelated cleanup. '
                      'The Astra coordinator owns substantive review and final acceptance. '
                      'Return a JSON object with status complete|partial|blocked, summary string, '
                      'artifacts/checks/risks arrays of strings. Report concrete unresolved judgment calls.')
        job = {'id': 'adapter-' + arm, 'provider': 'codex', 'model': 'gpt-5.6-luna', 'effort': 'max',
               'cwd': str(task), 'profile': 'edit', 'prompt': assignment, 'trusted_context': True,
               'timeout_seconds': 900, 'artifacts': owned, 'protected_files': protected,
               'checks': [{'id': 'visible-contract', 'argv': check, 'timeout_seconds': 120}]}
        save(folder / 'worker-request.json', job)
        # Both workers receive exactly this task-level prompt, apart from checkout paths.
        # Keep the runner-generated contract unchanged in both launch routes.
        full_assignment = runner.prompt_for(job)
        (task / 'WORKER-ASSIGNMENT.txt').write_text(full_assignment, encoding='utf-8')
        shutil.copytree(policy, task / '.benchmark-policy', ignore=shutil.ignore_patterns('scripts'))
        ticket = state / '.host-tickets' / job['id'] / 'ticket.json'
        common = (f'You are the benchmark coordinator, gpt-6-astra at high. Keep this configuration. '
                  f'Complete TASK.md in {task}. Use the frozen skill .benchmark-policy/SKILL.md and its directed references. '
                  'Exactly one gpt-5.6-luna/max worker attempt is required for the complete adapter batch. '
                  'Read WORKER-ASSIGNMENT.txt and do not change the assignment or acceptance criteria. '
                  'The worker owns implementation until its terminal handoff. Do not duplicate its investigation while it runs. '
                  'You own substantive review against TASK.md and final acceptance. After the worker stops you may make '
                  'necessary corrections locally, with affected rechecks, within this same run. No worker retries, '
                  'follow-up worker turns, extra agents, reviewer substitutions or external services. '
                  f'Use {sys.executable} -B -X utf8 for Python. '
                  'Read only this checkout plus explicitly allowed bridge/receipt files. Do not inspect personal skills, '
                  'memory, logs, other trials, reference solutions or held-out graders. '
                  'Use supported completion waits without unnecessary status polling. '
                  'Final response: accepted or not, actual checks, substantive review coverage and unresolved issues.\n')
        if arm == 'native':
            route = ('Use native spawn_agent, model="gpt-5.6-luna", reasoning_effort="max", fork_turns="none". '
                     'Pass the exact text of WORKER-ASSIGNMENT.txt as its message; no inherited history or added instructions. '
                     'Wait for terminal completion. You own the visible-contract final check: run '
                     + subprocess.list2cmdline(check) + ' in this checkout after completion, then review the result.\n')
        else:
            client = [sys.executable, '-B', '-X', 'utf8', str(policy / 'scripts/deployment_host.py'),
                      'request', str(ticket), '--wait-seconds', '1050']
            route = ('Native delegation is disabled. The authenticated host has already armed the exact assignment. '
                     'Trigger it once through this shell command: ' + subprocess.list2cmdline(client) + '. '
                     'Use shell quoting appropriate to PowerShell. Host scripts, the ticket and returned receipt/handoff '
                     'paths are allowed reads outside this checkout. Do not re-arm or alter the request. '
                     'The software runner owns the visible-contract final check; reuse its evidence, then review the result.\n')
        prompt = common + route
        (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
        flags = overrides(arm == 'native', disabled)
        command = [str(BINARY), 'exec', '--ignore-user-config', '--ignore-rules', '--strict-config',
                   '--json', '--color', 'never', '-s', 'workspace-write', '-m', 'gpt-6-astra', '-C', str(task), *flags, '-']
        save(folder / 'command.json', command)
        debug = observed([str(BINARY), *flags, 'debug', 'prompt-input', prompt], folder, 'prompt-inspection', cwd=task, timeout=60)
        assert debug['exit_code'] == 0 and '### Available skills' not in debug['stdout'], 'Coordinator isolation'
        runner.validate(job)
        runner.preflight(str(BINARY), job, runner.worker_env('codex'))
        save(folder / 'initial-hashes.json', {str(p.relative_to(task)): sha(p) for p in task.rglob('*')
                                             if p.is_file() and '.git' not in p.parts})
    fixture['frozen'] = tracked_files(fixture)
    save(root / 'manifest.json', fixture)
    save(POINTER, {'root': str(root)})
    print(json.dumps({'prepared': str(root), 'reference_and_stub_qualified': True, 'paid_calls': 0}), flush=True)


def run():
    root = Path(read(POINTER)['root'])
    fixture = read(root / 'manifest.json')
    assert fixture['frozen'] == tracked_files(fixture), 'Frozen evidence changed'
    with (root / 'started.json').open('x') as marker:
        json.dump({'time': time.time(), 'order': fixture['order']}, marker)
    env = dict(runner.worker_env('codex'), PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    for arm in fixture['order']:
        assert fixture['frozen'] == tracked_files(fixture)
        folder, host = root / arm, None
        task = folder / 'task'
        for name, digest in read(folder / 'initial-hashes.json').items():
            assert sha(task / name) == digest, 'Starting checkout changed'
        print(json.dumps({'starting': arm, 'directory': str(folder)}), flush=True)
        host_streams = []
        try:
            if arm == 'software':
                host_streams = [(folder / ('host.' + name)).open('wb') for name in ('stdout', 'stderr')]
                cmd = [sys.executable, '-B', '-X', 'utf8', str(Path(fixture['policy']) / 'scripts/deployment_host.py'),
                       'serve', str(folder / 'worker-request.json'), '--state-dir', fixture['state'],
                       '--bridge-dir', str(task / '.bridge'), '--codex', str(BINARY), '--trigger-timeout-seconds', '300']
                host = subprocess.Popen(cmd, stdout=host_streams[0], stderr=host_streams[1], stdin=subprocess.DEVNULL,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
                ticket = Path(fixture['state']) / '.host-tickets/adapter-software/ticket.json'
                deadline = time.monotonic() + 30
                while not ticket.exists():
                    if host.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('Host did not arm; no coordinator started')
                    time.sleep(.1)
                probe = ("from pathlib import Path; import sys; p=Path(sys.argv[1]); assert p.is_file(); "
                         "\ntry: (p.parent/'write-probe').write_text('unsafe')"
                         "\nexcept PermissionError: print('write-denied')"
                         "\nelse: raise SystemExit('UNSAFE')")
                probe_cmd = sandbox(task, [sys.executable, '-B', '-c', probe, str(ticket)])
                probe_cmd[probe_cmd.index(':read-only')] = ':workspace'
                assert observed(probe_cmd, folder, 'private-state-probe')['exit_code'] == 0
            started = time.monotonic()
            timed_out = False
            with (folder / 'events.jsonl').open('wb') as out, (folder / 'stderr.log').open('wb') as err:
                proc = subprocess.Popen(read(folder / 'command.json'), cwd=task, env=env, stdin=subprocess.PIPE,
                                        stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
                save(folder / 'process.json', {'pid': proc.pid})
                try:
                    proc.communicate((folder / 'prompt.txt').read_bytes(), timeout=1200)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    runner.claude_worker.stop_tree(proc)
                    proc.wait(timeout=20)
            if host:
                try:
                    host.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    raise RuntimeError('Coordinator ended with host still active; inspect before continuing')
            result = {'arm': arm, 'exit_code': proc.returncode, 'timed_out': timed_out,
                      'seconds': round(time.monotonic() - started, 3)}
            for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines():
                event = json.loads(line)
                if event.get('type') == 'thread.started':
                    result['thread_id'] = event['thread_id']
            grade = observed(sandbox(task, [sys.executable, '-B', '-X', 'utf8', str(SUITE / 'grade.py'), str(task)]), folder, 'grade')
            result['grade_exit_code'] = grade['exit_code']
            if arm == 'software':
                result['worker_receipt'] = str(Path(fixture['state']) / 'adapter-software/receipt.json')
            save(folder / 'result.json', result)
            print(json.dumps(result), flush=True)
            if timed_out or proc.returncode != 0:
                raise RuntimeError('Infrastructure/timeout failure; no automatic continuation')
        finally:
            if host and host.poll() is None:
                runner.claude_worker.stop_tree(host)
                host.wait(timeout=20)
            for stream in host_streams:
                stream.close()
    assert fixture['frozen'] == tracked_files(fixture)


def summarize():
    root = Path(read(POINTER)['root'])
    spec = importlib.util.spec_from_file_location('accounting', HERE.parent / 'revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    index = accounting.session_index()
    rows = []
    for arm in ('native', 'software'):
        result = read(root / arm / 'result.json')
        tids = {result['thread_id']}
        if arm == 'software':
            tids.add(read(result['worker_receipt'])['worker']['session_id'])
        while True:
            found = {tid for tid, meta in index.items() if meta['parent'] in tids}
            if found <= tids:
                break
            tids |= found
        agents = [accounting.audit_thread(tid, index[tid]) for tid in sorted(tids)]
        assert all(a.get('reconciled') for a in agents), 'Incomplete accounting'
        row = dict(result, agents=agents, api_equivalent_usd=sum(a['api_equivalent_usd'] for a in agents))
        rows.append(row)
        print(json.dumps({'arm': arm, 'api_equivalent_usd': row['api_equivalent_usd'],
                          'agents': len(agents), 'grade_exit_code': result['grade_exit_code']}))
    save(root / 'accounting.json', {'runs': rows, 'rates_per_million': accounting.RATES,
                                  'note': 'Frozen historical API-equivalent rates, not allowance. Research setup/supervision and external grading excluded.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'run', 'summarize'))
    globals()[parser.parse_args().operation]()
