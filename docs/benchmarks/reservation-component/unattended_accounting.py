"""Own-task setup/review usage snapshot; no model calls or transcript export."""
from collections import Counter
import importlib.util
from pathlib import Path

from experiment import REPO, read, save
from unattended import POINTER, launch_identity


def snapshot(identity, rates):
    contexts, records, completions = {}, {}, set()
    last_time = None
    for row in rates.entries(Path(identity['rollout'])):
        p = row.get('payload', {})
        if row.get('type') == 'turn_context':
            contexts[p.get('turn_id')] = p
        elif row.get('type') == 'token_usage_record' and p.get('thread_id') == identity['thread_id']:
            if p.get('turn_id') == identity['turn_id']:
                records[p['response_id']] = p
                last_time = row.get('timestamp')
        elif row.get('type') == 'event_msg' and p.get('type') == 'task_complete':
            completions.add(p.get('turn_id'))
    context = contexts.get(identity['turn_id'], {})
    totals = Counter()
    amount = 0.0
    known = context.get('model') in rates.RATES and context.get('service_tier') in (None, 'default', 'standard')
    for record in records.values():
        usage = record['usage']
        totals.update({f: usage.get(f, 0) for f in rates.FIELDS})
        inp, cached, written, out = (usage.get(f, 0) for f in rates.FIELDS[:4])
        assert inp >= cached + written
        if known:
            ri, rc, rw, ro = rates.RATES[context['model']]
            if inp > 272000:
                ri, rc, rw, ro = ri*2, rc*2, rw*2, ro*1.5
            amount += ((inp-cached-written)*ri+cached*rc+written*rw+out*ro)/1e6
    return {**identity, 'model': context.get('model'), 'effort': context.get('effort'),
            'service_tier': context.get('service_tier'), 'responses': len(records),
            'usage': dict(totals), 'api_equivalent_usd': amount if known and records else None,
            'completion_event_observed': identity['turn_id'] in completions,
            'last_usage_timestamp': last_time}


def main():
    root = Path(read(POINTER)['root'])
    spec = importlib.util.spec_from_file_location('rates', REPO/'docs/benchmarks/revision-ab/summarize.py')
    rates = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rates)
    setup = read(root/'manifest.json')['setup_turn']
    review = launch_identity()
    assert setup['turn_id'] != review['turn_id']
    result = {'setup': snapshot(setup, rates), 'review_snapshot': snapshot(review, rates),
              'limits': 'Recorded completed responses only. Current review excludes subsequent/in-flight usage. Prior fixture research and machine costs excluded. Historical API-equivalent rates, not bills. No allocation between arms.'}
    save(root/'unattended-supervision.json', result)
    for label in ('setup', 'review_snapshot'):
        row = result[label]
        print(label, {k: row[k] for k in ('model','effort','responses','api_equivalent_usd','completion_event_observed','last_usage_timestamp')})


if __name__ == '__main__':
    main()
