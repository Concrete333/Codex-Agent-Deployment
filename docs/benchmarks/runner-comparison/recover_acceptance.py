"""Revalidate the completed attempt-02 worker and run its previously unstarted acceptance once."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import host_pipeline as pipeline

pipeline.ARM = 'host-pipeline-02'
trial = pipeline.trial


def inputs():
    root, folder, original = pipeline.locations()
    job = trial.read(folder / 'worker-request.json')
    state = Path(original['state'])
    old = state / job['id']
    recovery = folder / 'acceptance-recovery'
    return root, folder, job, old, recovery


def prepare():
    root, folder, job, old, recovery = inputs()
    original = trial.read(old / 'receipt.json')
    assert not trial.read(folder / 'result.json')['acceptance_started']
    assert original['status'] == 'blocked' and original['error'].startswith('PermissionError:')
    assert original['worker_process']['exit_code'] == 0 and not original['worker_process']['timed_out']
    assert not any(trial.runner.pid_alive(pid) for pid in [original['runner_pid'], *original['process_pids']])
    handoff, metadata, status = trial.runner.parse_worker(job, old, original['worker_process'])
    assert status == 'complete' and metadata['session_id'] == original['worker']['session_id']
    assert original['request_sha256'] == trial.runner.digest(job)
    assert original['protected_sha256'] == trial.runner.protected_hashes(job)
    recovery.mkdir(exist_ok=False)
    binary = str(trial.BINARY)
    artifacts = trial.runner.fingerprints(job, binary)
    assert artifacts == original['artifact_sha256']
    claimed = trial.runner.handoff_fingerprints(job, handoff, binary)
    checks = []
    for check in job['checks']:
        observed = trial.observed(trial.runner.build_check(binary, job, check), recovery,
                                   'check-' + check['id'], cwd=job['cwd'], timeout=check['timeout_seconds'])
        assert observed['exit_code'] == 0, observed
        checks.append(dict(observed, id=check['id'], status='passed'))
    receipt = dict(original, status='ready_for_review', error=None, ownership_check_required=False,
                   checks=checks, artifact_sha256=artifacts,
                   artifact_sha256_after_checks=trial.runner.fingerprints(job, binary),
                   handoff_artifact_sha256=claimed,
                   revalidation_note='Offline sandbox hashing after host PermissionError; original receipt preserved',
                   original_receipt_path=str(old / 'receipt.json'))
    trial.runner.verify_review_evidence(job, receipt, handoff, binary)
    trial.save(recovery / 'receipt.json', receipt)
    trial.save(recovery / 'handoff.json', handoff)
    grade = trial.observed(trial.sandbox(job['cwd'], [sys.executable, '-B', '-X', 'utf8',
                            str(trial.SUITE / 'grade.py'), job['cwd']]), recovery, 'worker-grade')
    assert grade['exit_code'] == 0
    trial.runner.verify_review_evidence(job, receipt, handoff, binary)
    packet = {'handoff': handoff, 'status': receipt['status'],
              'checks': [{'id': c['id'], 'status': c['status'], 'exit_code': c['exit_code']} for c in checks],
              'artifact_sha256': artifacts, 'handoff_artifact_sha256': claimed,
              'protected_files_unchanged': True, 'accepted': False}
    trial.save(Path(job['cwd']) / 'ACCEPTANCE-PACKET.json', packet)
    frozen_paths = [Path(__file__), trial.REPO / 'scripts/deployment_runner.py',
                    trial.REPO / 'scripts/deployment_hash.py', trial.REPO / 'scripts/claude_worker.py',
                    folder / 'prompt.txt', folder / 'command.json', folder / 'worker-request.json',
                    old / 'receipt.json', old / 'handoff.json', recovery / 'receipt.json',
                    recovery / 'handoff.json', Path(job['cwd']) / 'ACCEPTANCE-PACKET.json']
    trial.save(recovery / 'manifest.json', {'frozen': {str(p): trial.sha(p) for p in frozen_paths},
               'paid_calls': 0, 'acceptance_timeout_seconds': 1200,
               'original_worker_reused': True, 'changes_to_worker_files': False})
    print(json.dumps({'revalidated': True, 'cases_passed': 244, 'paid_calls': 0}), flush=True)


def run():
    root, folder, job, old, recovery = inputs()
    manifest = trial.read(recovery / 'manifest.json')
    assert all(trial.sha(path) == digest for path, digest in manifest['frozen'].items())
    trial.runner.verify_review_evidence(job, trial.read(recovery / 'receipt.json'),
                                        trial.read(recovery / 'handoff.json'), str(trial.BINARY))
    with (recovery / 'started.json').open('x') as stream:
        json.dump({'started_at': time.time()}, stream)
    result = {'arm': 'host-pipeline-02', 'offline_recovery': True,
              'worker_receipt': str(old / 'receipt.json'), 'acceptance_started': True}
    proc = None
    started = time.monotonic()
    try:
        with (recovery / 'events.jsonl').open('wb') as out, (recovery / 'stderr.log').open('wb') as err:
            proc = subprocess.Popen(trial.read(folder / 'command.json'), cwd=job['cwd'],
                env=dict(trial.runner.worker_env('codex'), PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1'),
                stdin=subprocess.PIPE, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
            trial.save(recovery / 'process.json', {'pid': proc.pid})
            print(json.dumps({'stage': 'acceptance', 'model': 'gpt-6-astra', 'effort': 'high'}), flush=True)
            proc.communicate((folder / 'prompt.txt').read_bytes(), timeout=1200)
            result['exit_code'] = proc.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        result['error'] = str(exc)
    finally:
        if proc and proc.poll() is None:
            trial.runner.claude_worker.stop_tree(proc)
            proc.wait(timeout=20)
        result['seconds'] = round(time.monotonic() - started, 3)
        events = [json.loads(line) for line in (recovery / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
        result['thread_id'] = next((e['thread_id'] for e in events if e.get('type') == 'thread.started'), None)
        result['final_messages'] = [e['item']['text'] for e in events if e.get('type') == 'item.completed'
                                    and e['item'].get('type') == 'agent_message'][-1:]
        trial.save(recovery / 'result.json', result)
    grade = trial.observed(trial.sandbox(job['cwd'], [sys.executable, '-B', '-X', 'utf8',
                           str(trial.SUITE / 'grade.py'), job['cwd']]), recovery, 'grade')
    result['grade_exit_code'] = grade['exit_code']
    trial.save(recovery / 'result.json', result)
    print(json.dumps(result), flush=True)
    summarize()


def summarize():
    root, folder, job, old, recovery = inputs()
    result = trial.read(recovery / 'result.json')
    spec = importlib.util.spec_from_file_location('accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    index = accounting.session_index()
    worker_tid = trial.read(old / 'receipt.json')['worker']['session_id']
    tids = {worker_tid, result['thread_id']}
    while True:
        children = {tid for tid, meta in index.items() if meta['parent'] in tids}
        if children <= tids:
            break
        tids |= children
    agents = [accounting.audit_thread(tid, index[tid]) for tid in sorted(tids)]
    assert all(a.get('reconciled') for a in agents)
    total = sum(a['api_equivalent_usd'] for a in agents)
    prior = trial.read(root / 'host-pipeline-01/accounting.json')['api_equivalent_usd']
    report = dict(result, agents=agents, api_equivalent_usd=total,
                  including_prior_timeout_captured_usd=total + prior,
                  prior_timeout_captured_usd=prior, rates_per_million=accounting.RATES,
                  note='Offline recovery, not uninterrupted pipeline. Same completed worker and one fresh acceptance; no new worker call. Frozen API-equivalent rates, not allowance. Research setup/supervision and external grading excluded; prior timeout may omit in-flight usage.')
    trial.save(recovery / 'accounting.json', report)
    print(json.dumps({'api_equivalent_usd': total, 'including_prior_timeout_captured_usd': total + prior,
                      'agents': len(agents), 'grade_exit_code': result['grade_exit_code']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'run', 'summarize'))
    globals()[parser.parse_args().operation]()
