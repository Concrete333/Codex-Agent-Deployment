"""One explicitly authorized software-arm recovery; preserve the original pair."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import experiment as trial

RUNTIME = trial.REPO / 'scripts/deployment_host.py'
PWSH = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'


def locations():
    root = Path(trial.read(trial.POINTER)['root'])
    return root, root / 'software-recovery-02', trial.read(root / 'manifest.json')


def frozen(original):
    assert original['frozen'] == trial.tracked_files(original), 'Original comparison changed'
    scripts = ['deployment_host.py', 'deployment_runner.py', 'claude_worker.py']
    for name in scripts:
        if name != 'deployment_host.py':
            assert trial.sha(trial.REPO / 'scripts' / name) == trial.sha(Path(original['policy']) / 'scripts' / name), name
    return {str(trial.REPO / 'scripts' / name): trial.sha(trial.REPO / 'scripts' / name) for name in scripts}


def workspace(task, argv):
    cmd = trial.sandbox(task, argv)
    cmd[cmd.index(':read-only')] = ':workspace'
    return cmd


def ps_command(argv):
    return [str(PWSH), '-NoProfile', '-Command', '& ' + ' '.join("'" + str(a).replace("'", "''") + "'" for a in argv)]


def client(ticket, wait=1050):
    return [sys.executable, '-B', '-X', 'utf8', str(RUNTIME), 'request', str(ticket), '--wait-seconds', str(wait)]


def start_host(command, folder, prefix, ticket):
    streams = [(folder / (prefix + '.' + name)).open('wb') for name in ('stdout', 'stderr')]
    proc = None
    try:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=streams[0], stderr=streams[1],
                                creationflags=subprocess.CREATE_NO_WINDOW)
        trial.save(folder / (prefix + '-process.json'), {'pid': proc.pid})
        deadline = time.monotonic() + 30
        while not ticket.exists():
            if proc.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError(prefix + ' failed to arm')
            time.sleep(.1)
        return proc, streams
    except BaseException:
        stop_host(proc, streams)
        raise


def stop_host(proc, streams):
    if proc and proc.poll() is None:
        trial.runner.claude_worker.stop_tree(proc)
        proc.wait(timeout=20)
    for stream in streams:
        stream.close()


def prepare():
    root, folder, original = locations()
    runtime_hashes = frozen(original)
    folder.mkdir(exist_ok=False)
    task = folder / 'task'
    source = original['source_fixture']['source']
    shutil.copytree(source, task, ignore=shutil.ignore_patterns('__pycache__', '.git'))
    subprocess.run(['git', 'init', '-q', str(task)], check=True)
    observed = trial.observed(['git', '-C', str(task), 'add', '.'], folder, 'git-stage')
    assert observed['exit_code'] == 0
    old_task = root / 'software/task'
    job = trial.read(root / 'software/worker-request.json')
    job.update(id='adapter-software-recovery-02', cwd=str(task), prompt=job['prompt'].replace(str(old_task), str(task)))
    trial.runner.validate(job)
    trial.save(folder / 'worker-request.json', job)
    (task / 'WORKER-ASSIGNMENT.txt').write_text(trial.runner.prompt_for(job), encoding='utf-8')
    shutil.copytree(Path(original['policy']), task / '.benchmark-policy', ignore=shutil.ignore_patterns('scripts', '__pycache__'))
    state = Path(original['state'])
    ticket = state / '.host-tickets' / job['id'] / 'ticket.json'
    old_ticket = state / '.host-tickets/adapter-software/ticket.json'
    prompt = (root / 'software/prompt.txt').read_text(encoding='utf-8')
    prompt = prompt.replace(str(old_task), str(task)).replace(str(old_ticket), str(ticket))
    prompt = prompt.replace(str(Path(original['policy']) / 'scripts/deployment_host.py'), str(RUNTIME))
    (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
    command = [arg.replace(str(old_task), str(task)) for arg in trial.read(root / 'software/command.json')]
    trial.save(folder / 'command.json', command)
    # Exact runtime path, interpreter, shell and client sandbox. No model calls.
    check = trial.observed(workspace(task, ps_command([sys.executable, '-B', '-X', 'utf8', str(RUNTIME), '--help'])), folder, 'script-preflight')
    assert check['exit_code'] == 0
    trial.runner.preflight(str(trial.BINARY), job, trial.runner.worker_env('codex'))
    probe_job = dict(job, id='recovery-02-transport-probe')
    trial.save(folder / 'probe-request.json', probe_job)
    probe_ticket = state / '.host-tickets' / probe_job['id'] / 'ticket.json'
    host_cmd = [sys.executable, '-B', '-X', 'utf8', str(trial.REPO / 'tests/fixtures/host_fixture.py'),
                str(folder / 'probe-request.json'), str(state), str(task / '.bridge')]
    host, streams = start_host(host_cmd, folder, 'probe-host', probe_ticket)
    try:
        probe = ("from pathlib import Path; import sys; p=Path(sys.argv[1]); assert p.is_file(); "
                 "\ntry: (p.parent/'write-probe').write_text('unsafe')"
                 "\nexcept PermissionError: print('write-denied')"
                 "\nelse: raise SystemExit('UNSAFE')")
        observed = trial.observed(workspace(task, [sys.executable, '-B', '-c', probe, str(probe_ticket)]), folder, 'private-state-probe')
        assert observed['exit_code'] == 0 and 'write-denied' in observed['stdout']
        first = trial.observed(workspace(task, ps_command(client(probe_ticket, 30))), folder, 'client-preflight')
        assert first['exit_code'] == 0 and json.loads(first['stdout'])['offline_fixture'] is True
        host.wait(timeout=30)
        assert host.returncode == 0
        second = trial.observed(workspace(task, ps_command(client(probe_ticket, 30))), folder, 'repeat-client-preflight')
        assert second['exit_code'] == 0 and json.loads(second['stdout']) == json.loads(first['stdout'])
    finally:
        stop_host(host, streams)
    flags = command[command.index('-c'):-1]
    debug = trial.observed([str(trial.BINARY), *flags, 'debug', 'prompt-input', prompt], folder, 'prompt-inspection', cwd=task, timeout=60)
    assert debug['exit_code'] == 0 and '### Available skills' not in debug['stdout']
    initial = {str(p.relative_to(task)): trial.sha(p) for p in task.rglob('*') if p.is_file() and '.git' not in p.parts}
    manifest = {'runtime_hashes': runtime_hashes, 'initial_hashes': initial, 'recovery_script_sha256': trial.sha(__file__),
                'request_sha256': trial.sha(folder / 'worker-request.json'), 'prompt_sha256': trial.sha(folder / 'prompt.txt'),
                'command_sha256': trial.sha(folder / 'command.json'), 'original_root': str(root),
                'preflight_passed': True, 'paid_calls': 0,
                'change': 'Canonical runtime path; client endpoint identity validation without ancestor metadata access; fresh task and request identity'}
    trial.save(folder / 'manifest.json', manifest)
    print(json.dumps({'prepared': str(folder), 'full_fake_worker_transport': 'passed', 'paid_calls': 0}), flush=True)


def run():
    root, folder, original = locations()
    manifest = trial.read(folder / 'manifest.json')
    assert manifest['preflight_passed'] and manifest['runtime_hashes'] == frozen(original)
    assert manifest['recovery_script_sha256'] == trial.sha(__file__)
    for field, name in [('request', 'worker-request.json'), ('prompt', 'prompt.txt'), ('command', 'command.json')]:
        assert manifest[field + '_sha256'] == trial.sha(folder / name)
    task = folder / 'task'
    assert all(trial.sha(task / name) == digest for name, digest in manifest['initial_hashes'].items())
    with (folder / 'started.json').open('x') as stream:
        json.dump({'started_at': time.time(), 'authorized_recovery': True}, stream)
    job = trial.read(folder / 'worker-request.json')
    state = Path(original['state'])
    ticket = state / '.host-tickets' / job['id'] / 'ticket.json'
    host_cmd = [sys.executable, '-B', '-X', 'utf8', str(RUNTIME), 'serve', str(folder / 'worker-request.json'),
                '--state-dir', str(state), '--bridge-dir', str(task / '.bridge'), '--codex', str(trial.BINARY),
                '--trigger-timeout-seconds', '300']
    host, streams = start_host(host_cmd, folder, 'host', ticket)
    result = {'arm': 'software-recovery-02', 'worker_receipt': str(state / job['id'] / 'receipt.json')}
    proc = None
    started = time.monotonic()
    print(json.dumps({'starting': result['arm'], 'directory': str(folder)}), flush=True)
    try:
        with (folder / 'events.jsonl').open('wb') as out, (folder / 'stderr.log').open('wb') as err:
            env = dict(trial.runner.worker_env('codex'), PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
            proc = subprocess.Popen(trial.read(folder / 'command.json'), cwd=task, env=env, stdin=subprocess.PIPE,
                                    stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
            trial.save(folder / 'process.json', {'pid': proc.pid})
            proc.communicate((folder / 'prompt.txt').read_bytes(), timeout=1200)
        result['exit_code'] = proc.returncode
        host.wait(timeout=30)
        result['host_exit_code'] = host.returncode
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result['error'] = str(exc)
    finally:
        if proc and proc.poll() is None:
            trial.runner.claude_worker.stop_tree(proc)
            proc.wait(timeout=20)
        stop_host(host, streams)
        result['seconds'] = round(time.monotonic() - started, 3)
        for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines():
            event = json.loads(line)
            if event.get('type') == 'thread.started':
                result['thread_id'] = event['thread_id']
        trial.save(folder / 'result.json', result)
    grade = trial.observed(trial.sandbox(task, [sys.executable, '-B', '-X', 'utf8', str(trial.SUITE / 'grade.py'), str(task)]), folder, 'grade')
    result['grade_exit_code'] = grade['exit_code']
    trial.save(folder / 'result.json', result)
    assert manifest['runtime_hashes'] == frozen(original)
    print(json.dumps(result), flush=True)


def summarize():
    root, folder, original = locations()
    result = trial.read(folder / 'result.json')
    spec = importlib.util.spec_from_file_location('accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    index = accounting.session_index()
    tids = {result['thread_id']}
    if Path(result['worker_receipt']).exists():
        receipt = trial.read(result['worker_receipt'])
        if receipt.get('worker', {}).get('session_id'):
            tids.add(receipt['worker']['session_id'])
    while True:
        children = {tid for tid, meta in index.items() if meta['parent'] in tids}
        if children <= tids:
            break
        tids |= children
    agents = [accounting.audit_thread(tid, index[tid]) for tid in sorted(tids)]
    assert all(a.get('reconciled') for a in agents)
    total = sum(a['api_equivalent_usd'] for a in agents)
    prior = trial.read(root / 'postflight-accounting.json')['runs']
    native = next(r['api_equivalent_usd'] for r in prior if r['arm'] == 'native')
    failed = next(r['api_equivalent_usd'] for r in prior if r['arm'] == 'software')
    report = dict(result, agents=agents, api_equivalent_usd=total, native_baseline_usd=native,
                  earlier_failed_software_usd=failed, software_including_failed_launch_usd=total + failed,
                  rates_per_million=accounting.RATES,
                  note='Recovered arm, not an uninterrupted pair. Research setup/supervision and external evaluation excluded; not allowance.')
    trial.save(folder / 'accounting.json', report)
    print(json.dumps({key: value for key, value in report.items() if key not in ('agents', 'rates_per_million')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'run', 'summarize'))
    globals()[parser.parse_args().operation]()
