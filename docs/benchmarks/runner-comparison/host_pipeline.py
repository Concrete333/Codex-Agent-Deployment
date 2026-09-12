"""One frozen host-run worker, then fresh Astra High acceptance; no automatic retries."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import experiment as trial

ARM = 'host-pipeline-01'


def locations():
    root = Path(trial.read(trial.POINTER)['root'])
    return root, root / ARM, trial.read(root / 'manifest.json')


def runtime_hashes():
    return {str(path): trial.sha(path) for path in [Path(__file__),
            trial.REPO / 'scripts/deployment_runner.py', trial.REPO / 'scripts/deployment_hash.py',
            trial.REPO / 'scripts/claude_worker.py']}


def prepare():
    root, folder, original = locations()
    assert original['frozen'] == trial.tracked_files(original), 'Frozen comparison changed'
    folder.mkdir(exist_ok=False)
    task = folder / 'task'
    shutil.copytree(original['source_fixture']['source'], task,
                    ignore=shutil.ignore_patterns('__pycache__', '.git'))
    subprocess.run(['git', 'init', '-q', str(task)], check=True)
    subprocess.run(['git', '-C', str(task), 'add', '.'], check=True)
    old_task = root / 'software/task'
    job = trial.read(root / 'software/worker-request.json')
    worker_timeout = 900 if ARM == 'host-pipeline-01' else 1800
    job.update(id='adapter-' + ARM, cwd=str(task), timeout_seconds=worker_timeout,
               prompt=job['prompt'].replace(str(old_task), str(task)))
    # Saved requests are unnormalized; validate now so protected paths refer to this checkout.
    job = trial.runner.validate(job)
    trial.save(folder / 'worker-request.json', job)
    (task / 'WORKER-ASSIGNMENT.txt').write_text(trial.runner.prompt_for(job), encoding='utf-8')
    # Keep model-facing policy frozen, so this is not also a policy-ablation trial.
    shutil.copytree(original['policy'], task / '.benchmark-policy',
                    ignore=shutil.ignore_patterns('scripts', '__pycache__'))
    prompt = (f'You are the benchmark coordinator, gpt-6-astra at high. Keep this configuration. '
              f'Complete acceptance of TASK.md in {task}. Use the frozen skill '
              '.benchmark-policy/SKILL.md and its directed references. '
              'Exactly one gpt-5.6-luna/max worker has already finished the complete adapter batch. '
              'Read WORKER-ASSIGNMENT.txt and ACCEPTANCE-PACKET.json. Do not change the assignment '
              'or acceptance criteria. The software runner owns the visible-contract final check; '
              'reuse its evidence, then review the result. You own substantive review against TASK.md '
              'and final acceptance. You may make necessary corrections locally, with affected rechecks, '
              'within this same run. No worker retries, follow-up worker turns, extra agents, '
              'reviewer substitutions or external services. '
              f'Use {sys.executable} -B -X utf8 for Python. '
              'Read only this checkout. Do not inspect personal skills, memory, logs, other trials, '
              'reference solutions or held-out graders. '
              'Final response: accepted or not, actual checks, substantive review coverage and unresolved issues.')
    (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
    command = [arg.replace(str(old_task), str(task)) for arg in trial.read(root / 'software/command.json')]
    trial.save(folder / 'command.json', command)
    if ARM != 'host-pipeline-01':
        prior = root / ('host-pipeline-02' if ARM == 'host-pipeline-03' else 'host-pipeline-01')
        for name, current in [('prompt.txt', prompt),
                              ('task/WORKER-ASSIGNMENT.txt', trial.runner.prompt_for(job))]:
            assert current == (prior / name).read_text(encoding='utf-8').replace(str(prior / 'task'), str(task)), name
        assert command == [arg.replace(str(prior / 'task'), str(task))
                           for arg in trial.read(prior / 'command.json')]
    trial.runner.preflight(str(trial.BINARY), job, trial.runner.worker_env('codex'))
    flags = command[command.index('-c'):-1]
    debug = trial.observed([str(trial.BINARY), *flags, 'debug', 'prompt-input', prompt],
                           folder, 'prompt-inspection', cwd=task, timeout=60)
    assert debug['exit_code'] == 0 and '### Available skills' not in debug['stdout']
    # Exercise the exact final check command inside the real worker sandbox, without a model call.
    check = trial.observed(trial.runner.build_check(str(trial.BINARY), job, job['checks'][0]),
                           folder, 'stub-check-preflight', cwd=task)
    assert check['exit_code'] != 0 and 'Traceback' not in check['stderr'], check
    manifest = {'original_root': str(root), 'state': original['state'],
                'runtime_hashes': runtime_hashes(), 'preflight_passed': True,
                'initial_hashes': {str(p.relative_to(task)): trial.sha(p) for p in task.rglob('*')
                                  if p.is_file() and '.git' not in p.parts},
                'frozen_inputs': {name: trial.sha(folder / name) for name in
                                  ('worker-request.json', 'prompt.txt', 'command.json')},
                'change': 'Host launches worker/checks before fresh Astra High acceptance; artifact-path handoff clarification; no live coordinator during worker.',
                'worker_timeout_seconds': worker_timeout, 'acceptance_timeout_seconds': 1200,
                'paid_calls': 0, 'automatic_retry': False}
    trial.save(folder / 'manifest.json', manifest)
    print(json.dumps({'prepared': str(folder), 'paid_calls': 0}), flush=True)


def run():
    root, folder, original = locations()
    manifest = trial.read(folder / 'manifest.json')
    assert original['frozen'] == trial.tracked_files(original)
    assert manifest['runtime_hashes'] == runtime_hashes()
    assert all(trial.sha(folder / name) == digest for name, digest in manifest['frozen_inputs'].items())
    task = folder / 'task'
    assert all(trial.sha(task / name) == digest for name, digest in manifest['initial_hashes'].items())
    with (folder / 'started.json').open('x') as stream:
        json.dump({'started_at': time.time()}, stream)
    result = {'arm': ARM, 'acceptance_started': False, 'automatic_retry': False}
    started = time.monotonic()
    job = trial.read(folder / 'worker-request.json')
    state = Path(manifest['state'])
    result['worker_receipt'] = str(state / job['id'] / 'receipt.json')
    proc = None
    try:
        print(json.dumps({'stage': 'worker', 'model': job['model'], 'effort': job['effort']}), flush=True)
        worker = trial.runner.run(job, state, str(trial.BINARY))
        result['worker_status'] = worker['status']
        receipt, handoff = trial.runner.review_gate(job, state, str(trial.BINARY))
        # Independent grading is retained privately; never include it in the acceptance packet.
        pregrade = trial.observed(trial.sandbox(task, [sys.executable, '-B', '-X', 'utf8',
            str(trial.SUITE / 'grade.py'), str(task)]), folder, 'worker-grade')
        result['worker_grade_exit_code'] = pregrade['exit_code']
        # External grading must not have changed any acceptance evidence.
        trial.runner.review_gate(job, state, str(trial.BINARY))
        trial.save(task / 'ACCEPTANCE-PACKET.json', {
            'handoff': handoff, 'status': receipt['status'],
            'checks': [{'id': c['id'], 'status': c['status'], 'exit_code': c['exit_code']} for c in receipt['checks']],
            'artifact_sha256': receipt['artifact_sha256'],
            'handoff_artifact_sha256': receipt['handoff_artifact_sha256'],
            'protected_files_unchanged': True, 'accepted': False})
        result['worker_finished_at_unix'] = receipt['finished_at_unix']
        result['acceptance_started_at_unix'] = time.time()
        print(json.dumps({'stage': 'acceptance', 'model': 'gpt-6-astra', 'effort': 'high',
                          'worker_status': worker['status']}), flush=True)
        with (folder / 'events.jsonl').open('wb') as out, (folder / 'stderr.log').open('wb') as err:
            env = dict(trial.runner.worker_env('codex'), PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
            proc = subprocess.Popen(trial.read(folder / 'command.json'), cwd=task, env=env,
                                    stdin=subprocess.PIPE, stdout=out, stderr=err,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            result['acceptance_started'] = True
            trial.save(folder / 'process.json', {'pid': proc.pid})
            proc.communicate((folder / 'prompt.txt').read_bytes(), timeout=1200)
            result['exit_code'] = proc.returncode
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        if proc and proc.poll() is None:
            trial.runner.claude_worker.stop_tree(proc)
            proc.wait(timeout=20)
        result['seconds'] = round(time.monotonic() - started, 3)
        if (folder / 'events.jsonl').exists():
            events = [json.loads(line) for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
            result['thread_id'] = next((e['thread_id'] for e in events if e.get('type') == 'thread.started'), None)
            result['final_messages'] = [e['item']['text'] for e in events if e.get('type') == 'item.completed'
                                       and e['item'].get('type') == 'agent_message'][-1:]
        trial.save(folder / 'result.json', result)
    grade = trial.observed(trial.sandbox(task, [sys.executable, '-B', '-X', 'utf8',
        str(trial.SUITE / 'grade.py'), str(task)]), folder, 'grade')
    result['grade_exit_code'] = grade['exit_code']
    trial.save(folder / 'result.json', result)
    print(json.dumps(result), flush=True)
    summarize()


def summarize():
    root, folder, original = locations()
    result = trial.read(folder / 'result.json')
    spec = importlib.util.spec_from_file_location('accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    index = accounting.session_index()
    worker = trial.read(result['worker_receipt'])
    worker_tid = worker.get('worker', {}).get('session_id')
    if not worker_tid and worker.get('worker_process', {}).get('stdout_path'):
        worker_tid = trial.runner.interrupted_codex_session(worker['worker_process']['stdout_path'])
    if worker.get('worker_process', {}).get('pid') and not worker_tid:
        raise ValueError('Worker was launched but identity is missing; cost is unknown, not zero')
    tids = {tid for tid in (result.get('thread_id'), worker_tid) if tid}
    while True:
        children = {tid for tid, meta in index.items() if meta['parent'] in tids}
        if children <= tids:
            break
        tids |= children
    agents = [accounting.audit_thread(tid, index[tid]) for tid in sorted(tids)]
    assert all(a.get('reconciled') for a in agents), 'Accounting incomplete'
    report = dict(result, agents=agents, api_equivalent_usd=sum(a['api_equivalent_usd'] for a in agents),
                  usage_may_be_incomplete=bool(worker.get('worker_process', {}).get('timed_out')),
                  rates_per_million=accounting.RATES,
                  note='One fixed pipeline, not autonomous routing. Frozen historical API-equivalent rates, not allowance. Research setup/supervision and external grading excluded; no model planning stage in this arm.')
    trial.save(folder / 'accounting.json', report)
    print(json.dumps({'api_equivalent_usd': report['api_equivalent_usd'], 'agents': len(agents),
                      'acceptance_started': result['acceptance_started'], 'grade_exit_code': result['grade_exit_code']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'run', 'summarize'))
    parser.add_argument('--attempt', choices=('01', '02', '03'), default='01')
    args = parser.parse_args()
    ARM = 'host-pipeline-' + args.attempt
    globals()[args.operation]()
