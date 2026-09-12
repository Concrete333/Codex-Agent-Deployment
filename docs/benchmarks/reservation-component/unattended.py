"""Host-run frozen pair; save a compact packet for one later review in the original task."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import time

import experiment as base
import repeat

POINTER=base.HERE/'local-unattended.json'


def report(root,status,arms=None,error=None):
    value={'status':status,'accepted':False,'arms':arms or [],'error':error,
           'updated_at_unix':time.time(),'review':'One substantive acceptance review in the original task after completion; not automatically scheduled.'}
    base.save(root/'batch-status.json',value)
    lines=['# Unattended reservation batch','',f'Status: **{status}**','',
           'No result is accepted until the final source review.',
           'This file updates on disk; it does not send notifications or wake a model.','']
    for arm in value['arms']:
        amount=arm.get('api_equivalent_usd')
        price=f'${amount:.8f}' if amount is not None else 'usage unavailable'
        lines.append(f"- {arm['arm']}: {arm['status']}; {price}; {arm.get('attempts',0)} attempt(s).")
    if error: lines+=['','Error: '+str(error)]
    lines+=['','Costs are historical API-equivalent worker estimates, not bills.',
            'Setup and the later review are separate costs; no live supervisor should wait on this batch.',
            'When status is ready_for_review, ask the original Codex task to review this batch once.']
    (root/'STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def launch_identity():
    thread_id=os.environ.get('CODEX_THREAD_ID')
    paths=list((Path.home()/'.codex/sessions').glob(f'*/*/*/rollout-*{thread_id}*.jsonl')) if thread_id else []
    if not paths: return {'thread_id':thread_id,'usage_status':'unavailable'}
    path=max(paths,key=lambda p:p.stat().st_mtime); turn=None
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            try: row=json.loads(line)
            except ValueError: continue
            if row.get('type')=='turn_context': turn=row['payload'].get('turn_id')
    return {'thread_id':thread_id,'turn_id':turn,'rollout':str(path),
            'usage_status':'Account this exact setup turn after it finishes, then the later review turn separately.'}


def prepare():
    repeat.POINTER=POINTER
    repeat.prepare()  # Reuses byte checks, request equivalence and all offline qualification.
    root=Path(base.read(POINTER)['root'])
    manifest=base.read(root/'manifest.json')
    manifest['execution_mode']='Detached host batch; no live model supervisor; later single review in original task.'
    manifest['setup_turn']=launch_identity()
    base.save(root/'manifest.json',manifest)
    report(root,'prepared')
    print(json.dumps({'status_path':str(root/'STATUS.md'),'maximum_worker_sessions':4,
                      'review':'Deferred to the original task; no new Astra/Fable worker or automatic wakeup.'}))


def summarize_arms(root):
    data=base.read(root/'accounting.json')
    result=[]
    for arm in ['B','A']:
        attempts=[r for r in data['runs'] if r['arm']==arm]
        if not attempts:
            result.append({'arm':arm,'status':'not_run','attempts':0,'api_equivalent_usd':None}); continue
        complete=all(r['accounting'].get('reconciled') for r in attempts)
        result.append({'arm':arm,'status':attempts[-1]['status'],'attempts':len(attempts),
                       'api_equivalent_usd':sum(r['accounting']['api_equivalent_usd'] for r in attempts) if complete else None})
    return result


def run():
    base.POINTER=POINTER
    root=Path(base.read(POINTER)['root'])
    # Exclusive host guard complements the original driver's per-run and shared ownership guards.
    with (root/'host-started.json').open('x') as stream:
        json.dump({'pid':os.getpid(),'started_at_unix':time.time()},stream)
    report(root,'running')
    try:
        base.run()
        arms=summarize_arms(root)
        if not all(a['status']=='ready_for_review' for a in arms):
            report(root,'needs_attention',arms); return 1
        import review_saved
        review_saved.POINTER=POINTER
        for arm in ['B','A']:
            with contextlib.redirect_stdout(io.StringIO()):
                review_saved.main(arm)  # Hash/scope checks and added tests only; no semantic approval.
        import trace_metrics
        trace_metrics.POINTER=POINTER
        with contextlib.redirect_stdout(io.StringIO()): trace_metrics.main()
        report(root,'ready_for_review',arms)
        return 0
    except Exception as exc:
        # No retries, ownership bypass or model call for reporting failure.
        report(root,'needs_attention',error=f'{type(exc).__name__}: {exc}')
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['prepare','run'])
    args=parser.parse_args()
    if args.operation=='prepare': prepare()
    else: raise SystemExit(run())
