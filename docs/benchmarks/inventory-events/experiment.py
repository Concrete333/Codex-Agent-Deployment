"""Unattended solo-baseline/worker comparison. Exactly two attempts, no automatic repair."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'scripts'))
import deployment_runner as runner
import reference

POINTER=HERE/'local-fixture.json'
BINARY=Path.home()/'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
PROTECTED=['SPEC.md','AGENTS.md','tests/test_public.py','inventory/projection.py','inventory/__init__.py']
ARTIFACTS=['inventory/engine.py','inventory/ledger.py','inventory/api.py']
save=runner.atomic_json
read=runner.read_json


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def observed(job,check):
    done=subprocess.run(runner.build_check(str(BINARY),job,check),cwd=job['cwd'],
        env=dict(runner.worker_env('codex'),PYTHONDONTWRITEBYTECODE='1'),
        capture_output=True,text=True,encoding='utf-8',timeout=check['timeout_seconds'])
    return dict(exit_code=done.returncode,stdout=done.stdout,stderr=done.stderr)


def request(root,identity,arm):
    task=root/arm/'task'
    prompt=(f'Implement SPEC.md in this checkout. Own the complete inventory event component, '
            f'callers and focused tests. Use Python {sys.executable}. Read only this checkout. '
            'The host owns final independent checks and read-only acceptance against the same contract. '
            'Do not read evaluator/reference code or sibling attempts. Do not solve unrelated problems. ')
    job=dict(id=f'{identity}-{arm}',provider='codex',model='gpt-5.6-luna',effort='max',
        profile='edit',cwd=str(task),trusted_context=True,timeout_seconds=1800,
        prompt=prompt,artifacts=ARTIFACTS,protected_files=PROTECTED,
        checks=[dict(id='independent-contract',argv=[sys.executable,'-B',str(HERE/'grade.py'),str(task),
                      '--protected',str(root/'protected.json')],timeout_seconds=120)])
    job=runner.validate(job)
    if arm=='solo':
        # Standalone no-delegation benchmark owner, NOT an allowed deployment worker.
        # Production runner model validation and policy remain unchanged.
        job.update(model='gpt-6-astra',effort='high')
    return job


def status(root,value,error=None):
    save(root/'batch-status.json',dict(status=value,accepted=False,error=error,updated_at_unix=time.time()))
    (root/'STATUS.md').write_text(f'# Inventory-event comparison\n\nStatus: **{value}**\n\n'
        'Solo: Astra High, no delegation. Worker: Luna Max, one component owner.\n'
        'One attempt each; no automatic retry or acceptance. No notifications or model polling.\n'
        'Return to the original task for one read-only acceptance review when ready_for_review.\n'
        +(f'\nError: {error}\n' if error else ''),encoding='utf-8')


def prepare():
    if POINTER.exists(): raise ValueError('Existing preparation must be preserved')
    identity='inventory-'+uuid.uuid4().hex[:8]
    root=Path.home()/'AgentDeploymentBenchmarks'/identity
    root.mkdir(parents=True)
    prior=read(REPO/'docs/benchmarks/reservation-component/local-unattended.json')
    state=Path(read(Path(prior['root'])/'manifest.json')['state'])
    if (state/'active.json').exists(): raise ValueError('Shared active ownership unresolved')
    save(root/'protected.json',{p:sha(HERE/'task'/p) for p in PROTECTED})
    for arm in ['solo','worker']:
        shutil.copytree(HERE/'task',root/arm/'task',ignore=shutil.ignore_patterns('__pycache__'))
        subprocess.run(['git','init','-q',str(root/arm/'task')],check=True)
        job=request(root,identity,arm)
        runner.preflight(str(BINARY),job,runner.worker_env('codex'))
        save(root/arm/'request.json',job)
    # Qualified before any inference. Each mutant must be a real code change.
    variants={'reference':{},'starter':None,
        'alias_reference':{'ledger.py':reference.LEDGER.replace('from .projection import project','from .projection import project as view').replace('return project(', 'return view(')},
        'preview_commit':{'ledger.py':reference.LEDGER.replace('if not dry_run:', 'if True:')},
        'partial_stock_commit':{'ledger.py':reference.LEDGER.replace('step(stock, holds, event)','step(stock, holds, event)\n            self.balances = stock')},
        'input_alias':{'ledger.py':reference.LEDGER.replace('(dict(event), dict(receipt))','(event, dict(receipt))')},
        'receipt_alias':{'ledger.py':reference.LEDGER.replace('(dict(event), dict(receipt))','(dict(event), receipt)')},
        'replay_reapplied':{'ledger.py':reference.LEDGER.replace("if identity in seen:","if False:")},
        'reserved_transfer':{'engine.py':reference.ENGINE.replace('stock.get(key, 0) - held < n','stock.get(key, 0) < n')},
        'release_consumes':{'engine.py':reference.ENGINE.replace("if kind == 'ship':", "if kind in ('ship', 'release'):")},
        'bool_quantity':{'engine.py':reference.ENGINE.replace("type(event['quantity']) is not int", "not isinstance(event['quantity'], int)")}}
    qualified=[]
    for name,overrides in variants.items():
        target=root/'qualification'/name
        shutil.copytree(HERE/'task',target,ignore=shutil.ignore_patterns('__pycache__'))
        if overrides is not None:
            codes={'engine.py':reference.ENGINE,'ledger.py':reference.LEDGER,'api.py':reference.API}
            if name not in ('reference','alias_reference'):
                assert any(codes[k]!=v for k,v in overrides.items()),name
            for file,code in {**codes,**overrides}.items():
                (target/'inventory'/file).write_text(code,encoding='utf-8')
        job=read(root/'worker/request.json'); job['cwd']=str(target)
        check=dict(job['checks'][0]); check['argv']=[str(target) if a==str(root/'worker/task') else a for a in check['argv']]
        result=observed(job,check); save(root/'qualification'/f'{name}.json',result)
        expected=name in ('reference','alias_reference')
        if (result['exit_code']==0)!=expected: raise ValueError(f'Qualification {name}: {result}')
        qualified.append(dict(variant=name,exit_code=result['exit_code']))
    frozen={str(p):sha(p) for base in [HERE,root/'solo',root/'worker'] for p in base.rglob('*')
            if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p!=POINTER}
    for p in [root/'protected.json',REPO/'scripts/deployment_runner.py',REPO/'scripts/deployment_hash.py',
              REPO/'scripts/claude_worker.py',REPO/'docs/benchmarks/revision-ab/summarize.py']:
        frozen[str(p)]=sha(p)
    # Record the exact setup turn without exporting conversation content.
    thread=os.environ.get('CODEX_THREAD_ID')
    paths=list((Path.home()/'.codex/sessions').glob(f'*/*/*/rollout-*{thread}*.jsonl')) if thread else []
    setup=dict(thread_id=thread)
    if paths:
        path=max(paths,key=lambda p:p.stat().st_mtime); turn=None
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                try: row=json.loads(line)
                except ValueError: continue
                if row.get('type')=='turn_context': turn=row['payload'].get('turn_id')
        setup.update(turn_id=turn,rollout=str(path))
    manifest=dict(root=str(root),state=str(state),identity=identity,order=['solo','worker'],
                  frozen=frozen,qualification=qualified,maximum_sessions=2,setup_turn=setup)
    save(root/'manifest.json',manifest); save(POINTER,dict(root=str(root)))
    status(root,'prepared')
    print(json.dumps(dict(root=str(root),qualification=qualified,maximum_sessions=2)))


def solo(job,state):
    """Standalone solo baseline using shared process/ownership primitives, not worker routing."""
    assert job['model']=='gpt-6-astra' and job['effort']=='high' and job['id'].endswith('-solo')
    folder=state/job['id']; claim_path=state/'active.json'
    claim=dict(id=job['id'],runner_pid=os.getpid(),process_pids=[],phase='solo-baseline',cwd=job['cwd'])
    with claim_path.open('x') as stream: json.dump(claim,stream)
    released=False
    receipt=dict(id=job['id'],request_sha256=runner.digest(job),status='blocked',checks=[],ownership_check_required=False)
    try:
        folder.mkdir()
        save(folder/'request.json',job); save(folder/'handoff-schema.json',runner.SCHEMA)
        (folder/'prompt.txt').write_text(runner.prompt_for(job),encoding='utf-8')
        (folder/'empty-stdin.txt').write_text('',encoding='utf-8')
        command=runner.build_worker(str(BINARY),job,folder)
        save(folder/'command.json',command)
        receipt['protected_sha256']=runner.protected_hashes(job)
        runner.preflight(str(BINARY),job,runner.worker_env('codex'))
        def started(pid):
            claim['process_pids'].append(pid); save(claim_path,claim)
        process=runner.execute(command,job['cwd'],folder/'prompt.txt',folder/'solo',job['timeout_seconds'],runner.worker_env('codex'),started)
        receipt['worker_process']=process  # Existing accounting schema; role is solo baseline.
        if process['ownership_check_required']: raise RuntimeError('Solo cleanup uncertain; claim retained')
        handoff,metadata,value=runner.parse_worker(job,folder,process)
        receipt.update(worker=metadata,status=value)
        if value=='complete':
            receipt['artifact_sha256']=runner.fingerprints(job,str(BINARY))
            receipt['handoff_artifact_sha256']=runner.handoff_fingerprints(job,handoff,str(BINARY))
            for check in job['checks']:
                result=runner.execute(runner.build_check(str(BINARY),job,check),job['cwd'],folder/'empty-stdin.txt',
                    folder/('check-'+check['id']),check['timeout_seconds'],runner.worker_env('codex'),started)
                if result['ownership_check_required']: raise RuntimeError('Check cleanup uncertain; claim retained')
                result.update(id=check['id'],status='passed' if result['exit_code']==0 else 'failed')
                receipt['checks'].append(result)
            receipt['artifact_sha256_after_checks']=runner.fingerprints(job,str(BINARY))
            if (receipt['artifact_sha256']!=receipt['artifact_sha256_after_checks'] or
                receipt['handoff_artifact_sha256']!=runner.handoff_fingerprints(job,handoff,str(BINARY)) or
                receipt['protected_sha256']!=runner.protected_hashes(job)):
                raise ValueError('Protected evidence/artifacts changed during checks')
            receipt['status']='ready_for_review' if all(c['status']=='passed' for c in receipt['checks']) else 'checks_failed'
        released=True
    except BaseException as exc:
        receipt.update(status='blocked',error=str(exc),ownership_check_required=bool(claim['process_pids']))
        raise
    finally:
        receipt.update(runner_pid=claim['runner_pid'],process_pids=claim['process_pids'])
        if folder.is_dir(): save(folder/'receipt.json',receipt)
        if released: claim_path.unlink()
    return runner.compact(receipt,folder)


def packet(root,arm,job,state):
    receipt,handoff=runner.review_gate(job,state,str(BINARY))
    task=Path(job['cwd']); original=HERE/'task'
    allowed=lambda s: s in ARTIFACTS or (s.startswith('tests/test_worker') and s.endswith('.py') and s.count('/')==1)
    initial={p.relative_to(original).as_posix():sha(p) for p in original.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    current={p.relative_to(task).as_posix():sha(p) for p in task.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}
    changed=[p for p in initial.keys()|current.keys() if initial.get(p)!=current.get(p)]
    if any(not allowed(p) or p not in handoff['artifacts'] for p in changed): raise ValueError('Scope or handoff artifact gap')
    tests=observed(dict(job,profile='review'),dict(argv=[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_worker*.py','-q'],timeout_seconds=120))
    runner.review_gate(job,state,str(BINARY))
    save(root/arm/'review-packet.json',dict(checked_id=job['id'],handoff=handoff,changed=sorted(changed),
        fingerprints=receipt['handoff_artifact_sha256'],added_tests=tests,manual_review_required=True))
    if tests['exit_code']: raise ValueError('Added tests failed')


def summarize(root):
    spec=importlib.util.spec_from_file_location('cost',REPO/'docs/benchmarks/revision-ab/summarize.py')
    cost=importlib.util.module_from_spec(spec); spec.loader.exec_module(cost)
    index=cost.session_index(); rows=[]
    for arm in ['solo','worker']:
        result_path=root/arm/'result.json'
        if not result_path.exists(): continue
        result=read(result_path); receipt=read(Path(result['receipt_path']))
        tid=receipt.get('worker',{}).get('session_id')
        record=cost.audit_thread(tid,index[tid]) if tid in index else {'error':'Usage unavailable'}
        rows.append(dict(arm=arm,status=result['status'],accounting=record))
    save(root/'accounting.json',dict(rates=cost.RATES,runs=rows,excluded='Setup/fixture audit, later acceptance, failed setup and machine costs are separate, not free.'))
    for row in rows:
        expected=('gpt-6-astra','high') if row['arm']=='solo' else ('gpt-5.6-luna','max')
        record=row['accounting']
        if not record.get('reconciled') or {tuple(c) for c in record.get('configurations',[])}!={expected}:
            raise ValueError('Usage/configuration must be reconciled before reporting ready')


def run():
    root=Path(read(POINTER)['root']); manifest=read(root/'manifest.json'); state=Path(manifest['state'])
    if any(sha(p)!=digest for p,digest in manifest['frozen'].items()): raise ValueError('Frozen evidence changed')
    with (root/'started.json').open('x') as stream: json.dump(dict(pid=os.getpid(),time=time.time()),stream)
    status(root,'running')
    try:
        for arm in manifest['order']:
            job=read(root/arm/'request.json')
            result=solo(job,state) if arm=='solo' else runner.run(job,state,str(BINARY))
            save(root/arm/'result.json',result)
            print(json.dumps(dict(arm=arm,status=result['status'])),flush=True)
            if result['ownership_check_required'] or result['status'] in ('blocked','partial'):
                raise RuntimeError(f'{arm}: {result["status"]}; no automatic continuation')
            if result['status']=='ready_for_review': packet(root,arm,job,state)
        summarize(root)
        all_ready=all(read(root/arm/'result.json')['status']=='ready_for_review' for arm in manifest['order'])
        status(root,'ready_for_review' if all_ready else 'needs_attention')
    except BaseException as exc:
        status(root,'needs_attention',str(exc))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('operation',choices=['prepare','run','summarize'])
    args=parser.parse_args()
    if args.operation=='summarize': summarize(Path(read(POINTER)['root']))
    else: globals()[args.operation]()
