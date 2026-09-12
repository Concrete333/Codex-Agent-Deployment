"""Two explicitly authorized Astra High review-only sessions; no implementation or retry."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
import uuid

import experiment as base

HERE=Path(__file__).resolve().parent
POINTER=HERE/'local-acceptance.json'
runner=base.runner
read,save=base.read,base.save
PROMPT='''Review the supplied inventory component against SPEC.md. This is a read-only acceptance task: the implementation instructions inside the contract describe requirements, not permission to edit.
Read EVIDENCE.json, the full implementation, protected projection, exports, public tests and added tests. Verify atomic batches, all event effects, exact identities, replay and sequence state, isolation, shared-core preview, projection and API routing. Resolve implementation-reported risks against the contract and evidence.
The host has already run the listed checks and revalidated hashes. Reuse those results; do not rerun unchanged suites. A passing suite alone is not acceptance. You may run targeted, read-only Python probes with bytecode writing disabled for a concrete uncovered question. Do not create files, change source/tests, fix problems, read outside this checkout, delegate, use the network, or leave background commands running.
Report only material violations of settled contract requirements as findings, with path, line, trigger, impact and contract basis. Put unsettled interpretations in uncertainties instead of inventing requirements. Optional hardening is not a rejection reason. Return accept only after complete required inspection with no material defect or unresolved acceptance-blocking question. Return reject for demonstrated material defects; needs_clarification for a requirement ambiguity preventing acceptance. A limit or missing evidence is partial/blocked, not success.
Return JSON matching the supplied schema. Coverage lists the relative files you actually inspected. Keep the summary concise. Do not write the report into the checkout.
'''
SCHEMA={'type':'object','additionalProperties':False,'properties':{
    'status':{'type':'string','enum':['complete','partial','blocked']},
    'decision':{'type':'string','enum':['accept','reject','needs_clarification']},
    'summary':{'type':'string'},'coverage':{'type':'array','items':{'type':'string'}},
    'uncertainties':{'type':'array','items':{'type':'string'}},
    'findings':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{
        'file':{'type':'string'},'line':{'type':'integer','minimum':1},
        'trigger':{'type':'string'},'impact':{'type':'string'},'contract_basis':{'type':'string'}},
        'required':['file','line','trigger','impact','contract_basis']}}},
    'required':['status','decision','summary','coverage','uncertainties','findings']}


def tree(root):
    return {p.relative_to(root).as_posix():base.sha(p) for p in root.rglob('*')
            if p.is_file() and '.git' not in p.parts}


def validate_report(value,required):
    if not isinstance(value,dict) or set(value)!=set(SCHEMA['required']): raise ValueError('Invalid review fields')
    if value['status'] not in ('complete','partial','blocked') or value['decision'] not in ('accept','reject','needs_clarification'):
        raise ValueError('Invalid review status or decision')
    if not isinstance(value['summary'],str) or not value['summary'].strip(): raise ValueError('Empty summary')
    for key in ('coverage','uncertainties'):
        if not isinstance(value[key],list) or any(not isinstance(v,str) for v in value[key]): raise ValueError('Invalid '+key)
    if not isinstance(value['findings'],list): raise ValueError('Invalid findings')
    for finding in value['findings']:
        if not isinstance(finding,dict) or set(finding)!=set(SCHEMA['properties']['findings']['items']['required']): raise ValueError('Invalid finding')
        if type(finding['line']) is not int or finding['line']<1: raise ValueError('Invalid line')
        if any(not isinstance(finding[k],str) or not finding[k].strip() for k in ('file','trigger','impact','contract_basis')):
            raise ValueError('Empty finding evidence')
        if finding['file'] not in required: raise ValueError('Finding outside review scope')
    coverage={p.replace('\\','/').removeprefix('./') for p in value['coverage']}
    if value['status']=='complete' and not set(required)<=coverage: raise ValueError('Incomplete reported coverage')
    if value['decision']=='accept' and (value['status']!='complete' or value['findings']): raise ValueError('Unsupported acceptance')
    if value['decision']=='reject' and not value['findings']: raise ValueError('Rejection without a demonstrated finding')
    return value


def status(root,stage,error=None):
    save(root/'batch-status.json',dict(status=stage,error=error,updated_at_unix=time.time(),original_results_unchanged=True))
    (root/'STATUS.md').write_text(f'# Separate inventory acceptance costs\n\nStatus: **{stage}**\n\n'
        'Two fresh read-only Astra High review sessions. No implementation reruns or corrections.\n'
        'No model polling or automatic notification. Return to the original task when completed or needs_attention.\n'
        +(f'\nError: {error}\n' if error else ''),encoding='utf-8')


def prepare():
    if POINTER.exists(): raise ValueError('Existing acceptance preparation must be preserved')
    original=Path(read(base.POINTER)['root']); original_manifest=read(original/'manifest.json')
    state=Path(original_manifest['state'])
    if (state/'active.json').exists(): raise ValueError('Shared ownership unresolved')
    root=original.parent/('inventory-review-'+uuid.uuid4().hex[:8]); root.mkdir()
    arms=['solo','worker']; secrets.SystemRandom().shuffle(arms)
    cases=[]
    for label,arm in zip(['case-1','case-2'],arms):
        job=read(original/arm/'request.json')
        receipt,handoff=runner.review_gate(job,state,str(base.BINARY))
        original_task=Path(job['cwd']); task=root/label/'task'
        shutil.copytree(original_task,task,ignore=shutil.ignore_patterns('.git','__pycache__'))
        source={p:sha for p,sha in tree(original_task).items() if '__pycache__' not in Path(p).parts}
        assert tree(task)==source
        subprocess.run(['git','init','-q',str(task)],check=True)
        old_packet=read(original/arm/'review-packet.json')
        external=read(receipt['checks'][0]['stdout_path'])
        evidence={'contract':'SPEC.md','implementation_report':handoff,
                  'host_checks':{'independent':external,'added':old_packet['added_tests']},
                  'changed_files':old_packet['changed'],'checked_source_sha256':source,
                  'host_integrity':'Source and checked receipt hashes revalidated; no scope gaps.'}
        save(task/'EVIDENCE.json',evidence)
        required=sorted(p for p in source if p=='SPEC.md' or p.endswith('.py'))
        request=dict(id=root.name+'-'+label,provider='codex',model='gpt-6-astra',effort='high',profile='review',
            cwd=str(task),trusted_context=True,timeout_seconds=1200,prompt=PROMPT+f'Python executable: {sys.executable}.\n',
            artifacts=[],checks=[],protected_files=[str(task/p) for p in tree(task)])
        runner.preflight(str(base.BINARY),request,runner.worker_env('codex'))
        # Prove this native read-only sandbox rejects checkout writes before spending.
        probe="from pathlib import Path\ntry:\n Path('read-only-probe.txt').write_text('probe')\nexcept PermissionError:\n print('checkout write denied')\nelse:\n raise SystemExit('checkout unexpectedly writable')"
        observed=base.observed(request,dict(argv=[sys.executable,'-B','-c',probe],timeout_seconds=60))
        save(root/label/'sandbox-preflight.json',observed)
        if observed['exit_code'] or observed['stdout'].strip()!='checkout write denied': raise ValueError('Read-only sandbox preflight failed')
        save(root/label/'request.json',request)
        cases.append(dict(label=label,source_arm=arm,original_request=str(original/arm/'request.json'),
                          task_sha256=tree(task),required_coverage=required))
    # Capture the setup turn so research overhead can be counted after completion.
    identity={'thread_id':os.environ.get('CODEX_THREAD_ID')}
    paths=list((Path.home()/'.codex/sessions').glob(f'*/*/*/rollout-*{identity["thread_id"]}*.jsonl'))
    if paths:
        path=max(paths,key=lambda p:p.stat().st_mtime); turn=None
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                try: entry=json.loads(line)
                except ValueError: continue
                if entry.get('type')=='turn_context': turn=entry['payload'].get('turn_id')
        identity.update(turn_id=turn,rollout=str(path))
    files=[Path(__file__),HERE/'acceptance-protocol.md',HERE/'experiment.py',HERE/'grade.py',
           base.REPO/'scripts/deployment_runner.py',base.REPO/'scripts/deployment_hash.py',
           base.REPO/'scripts/claude_worker.py',HERE.parent/'revision-ab/summarize.py']
    files += [root/c['label']/'request.json' for c in cases]
    manifest=dict(root=str(root),original=str(original),state=str(state),cases=cases,setup_turn=identity,
                  frozen={str(p):base.sha(p) for p in files},maximum_sessions=2,
                  authorization='User explicitly approved two benchmark-only Astra High reviewer sessions; operational skill unchanged.')
    save(root/'manifest.json',manifest); save(POINTER,dict(root=str(root))); status(root,'prepared')
    print(json.dumps(dict(root=str(root),reviews=2,read_only_preflights='passed')))


def review(root,case,state):
    job=read(root/case['label']/'request.json'); task=Path(job['cwd']); folder=state/job['id']
    assert (job['model'],job['effort'],job['profile'])==('gpt-6-astra','high','review')
    if tree(task)!=case['task_sha256']: raise ValueError('Frozen review input changed')
    runner.review_gate(read(case['original_request']),state,str(base.BINARY))
    claim_path=state/'active.json'
    claim=dict(id=job['id'],runner_pid=os.getpid(),process_pids=[],phase='authorized-review-only',cwd=str(task))
    with claim_path.open('x') as stream: json.dump(claim,stream)
    released=False
    receipt=dict(id=job['id'],status='blocked',ownership_check_required=False)
    try:
        folder.mkdir(); save(folder/'request.json',job); save(folder/'handoff-schema.json',SCHEMA)
        (folder/'prompt.txt').write_text(job['prompt'],encoding='utf-8')
        command=runner.build_worker(str(base.BINARY),job,folder)
        save(folder/'command.json',command)
        def started(pid):
            claim['process_pids'].append(pid); save(claim_path,claim)
        process=runner.execute(command,str(task),folder/'prompt.txt',folder/'review',1200,runner.worker_env('codex'),started)
        receipt['process']=process
        if process['ownership_check_required']: raise RuntimeError('Review cleanup uncertain')
        released=True
        turns=[]; errors=[]; tid=None
        with Path(process['stdout_path']).open(encoding='utf-8') as stream:
            for line in stream:
                if not line.strip(): continue
                event=json.loads(line)
                if event.get('type')=='thread.started': tid=event['thread_id']
                elif event.get('type')=='turn.completed': turns.append(event.get('usage'))
                elif event.get('type') in ('error','turn.failed'): errors.append(event)
        receipt.update(thread_id=tid,reported_usage=turns,errors=errors)
        if process['exit_code'] or errors or len(turns)!=1 or not tid: raise ValueError('Review did not complete normally')
        if tree(task)!=case['task_sha256']: raise ValueError('Review changed frozen files')
        decision=validate_report(read(folder/'handoff.json'),case['required_coverage'])
        receipt.update(status='completed' if decision['status']=='complete' else 'needs_attention',report=decision,
                       original_files_unchanged=True)
    except BaseException as exc:
        receipt.update(error=str(exc),ownership_check_required=bool(claim['process_pids']) and not released)
        raise
    finally:
        receipt.update(runner_pid=os.getpid(),process_pids=claim['process_pids'])
        if folder.is_dir(): save(folder/'receipt.json',receipt)
        save(root/case['label']/'result.json',receipt)
        if released: claim_path.unlink()
    return receipt


def summarize(root,manifest):
    spec=importlib.util.spec_from_file_location('cost',HERE.parent/'revision-ab/summarize.py')
    cost=importlib.util.module_from_spec(spec); spec.loader.exec_module(cost)
    index=cost.session_index(); implementations=read(Path(manifest['original'])/'accounting.json')
    rows=[]
    for case in manifest['cases']:
        result=read(root/case['label']/'result.json'); tid=result['thread_id']
        usage=cost.audit_thread(tid,index[tid])
        if not usage.get('reconciled') or {tuple(c) for c in usage['configurations']}!={('gpt-6-astra','high')}:
            raise ValueError('Review usage/configuration mismatch')
        impl=next(r['accounting']['api_equivalent_usd'] for r in implementations['runs'] if r['arm']==case['source_arm'])
        rows.append(dict(case=case['label'],source_arm=case['source_arm'],decision=result['report']['decision'],
                         implementation_usd=impl,review_accounting=usage,
                         implementation_plus_review_usd=impl+usage['api_equivalent_usd']))
    save(root/'accounting.json',dict(runs=rows,rates=cost.RATES,
        limits='Retrospective saved implementation plus fresh review, not a new full pipeline. Setup/research, prior acceptance and later adjudication excluded from these per-arm figures and counted separately. Historical API-equivalent rates, not bills. Reviewer conclusions need adjudication.'))


def run():
    root=Path(read(POINTER)['root']); manifest=read(root/'manifest.json')
    if any(base.sha(p)!=sha for p,sha in manifest['frozen'].items()): raise ValueError('Frozen protocol/runtime changed')
    with (root/'started.json').open('x') as stream: json.dump(dict(pid=os.getpid(),time=time.time()),stream)
    status(root,'running')
    try:
        for case in manifest['cases']:
            result=review(root,case,Path(manifest['state']))
            if result['status']!='completed': raise RuntimeError('Incomplete review; no further paid calls')
        summarize(root,manifest); status(root,'completed')
    except BaseException as exc:
        status(root,'needs_attention',str(exc)); raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('operation',choices=['prepare','run','summarize'])
    args=parser.parse_args()
    if args.operation=='summarize':
        root=Path(read(POINTER)['root']); summarize(root,read(root/'manifest.json'))
    else: globals()[args.operation]()
