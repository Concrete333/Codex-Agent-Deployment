"""Point-in-time own-turn usage, separate from worker comparison. No model calls."""
from collections import Counter
import json
import os
from pathlib import Path
import importlib.util

from repeat import POINTER
from experiment import REPO, read, save


def main():
    thread_id=os.environ.get('CODEX_THREAD_ID')
    paths=list((Path.home()/'.codex/sessions').glob(f'*/*/*/rollout-*{thread_id}*.jsonl')) if thread_id else []
    if not paths: raise ValueError('Current task rollout unavailable')
    path=max(paths,key=lambda p:p.stat().st_mtime)
    contexts={}; records={}; latest_turn=None; last_time=None
    # Do not print transcript, instructions, reasoning or tool contents.
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            try: row=json.loads(line)
            except ValueError: continue
            p=row.get('payload',{})
            if row.get('type')=='turn_context':
                latest_turn=p.get('turn_id'); contexts[latest_turn]=p
            elif row.get('type')=='token_usage_record' and p.get('thread_id')==thread_id:
                records[p['response_id']]=p
            last_time=row.get('timestamp',last_time)
    selected=[r for r in records.values() if r.get('turn_id')==latest_turn]
    context=contexts.get(latest_turn,{})
    spec=importlib.util.spec_from_file_location('frozen_rates',REPO/'docs/benchmarks/revision-ab/summarize.py')
    accounting=importlib.util.module_from_spec(spec); spec.loader.exec_module(accounting)
    totals=Counter(); cost=0.0
    for record in selected:
        usage=record['usage']; totals.update({f:usage.get(f,0) for f in accounting.FIELDS})
        inp,cached,written,out=[usage.get(f,0) for f in accounting.FIELDS[:4]]
        if context.get('model') not in accounting.RATES or context.get('service_tier') not in (None,'default','standard'):
            cost=None; continue
        ri,rc,rw,ro=accounting.RATES[context['model']]
        if inp>272000: ri,rc,rw,ro=ri*2,rc*2,rw*2,ro*1.5
        if cost is not None: cost+=((inp-cached-written)*ri+cached*rc+written*rw+out*ro)/1e6
    result={'thread_id':thread_id,'turn_id':latest_turn,'rollout':str(path),'last_observed_timestamp':last_time,
        'model':context.get('model'),'effort':context.get('effort'),'responses':len(selected),'usage':dict(totals),
        'api_equivalent_usd':cost if selected else None,
        'scope':'Recorded completed responses of current supervisor turn only. Excludes subsequent/in-flight usage, prior preparation turns, and workers. Historical rate estimate, not a bill; not allocated between arms.'}
    root=Path(read(POINTER)['root']); save(root/'supervision-snapshot.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('rollout','thread_id','turn_id')}))


if __name__=='__main__': main()
