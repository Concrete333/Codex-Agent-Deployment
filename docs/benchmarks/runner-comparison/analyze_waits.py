"""Descriptive phase accounting from captured response records; no causal attribution."""
from collections import Counter
from datetime import datetime
import json
from pathlib import Path

import experiment as trial


def entries(path):
    with Path(path).open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


def analyze(parent, worker):
    worker_events = entries(worker['rollout'])
    bounds = [e['timestamp'] for e in worker_events if e['type'] == 'event_msg' and e['payload'].get('type') in ('task_started', 'task_complete')]
    start, end = min(bounds), max(bounds)
    data = entries(parent['rollout'])
    phases = {name: {'responses': 0, 'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0, 'usd': 0.0}
              for name in ('before_worker', 'while_worker_active', 'after_worker')}
    records = {e['payload']['response_id']: e for e in data if e['type'] == 'token_usage_record'
               and e['payload'].get('thread_id') == parent['thread_id']}
    for entry in records.values():
        phase = 'before_worker' if entry['timestamp'] < start else 'after_worker' if entry['timestamp'] > end else 'while_worker_active'
        out = phases[phase]
        u = entry['payload']['usage']
        out['responses'] += 1
        for key in ('input_tokens', 'cached_input_tokens', 'output_tokens'):
            out[key] += u.get(key, 0)
        uncached = u['input_tokens'] - u['cached_input_tokens'] - u.get('cache_write_input_tokens', 0)
        # All observed parent contexts are Astra High, standard tier, below long-context threshold.
        out['usd'] += (uncached * 10 + u['cached_input_tokens'] + u.get('cache_write_input_tokens', 0) * 12.5 + u['output_tokens'] * 50) / 1e6
    assert abs(sum(p['usd'] for p in phases.values()) - parent['api_equivalent_usd']) < 1e-8
    waits = []
    outputs = {}
    for e in data:
        p = e.get('payload', {})
        if e['type'] != 'response_item':
            continue
        if p.get('type') in ('function_call_output', 'custom_tool_call_output'):
            outputs[p.get('call_id')] = p.get('output', '')
        if p.get('type') in ('function_call', 'custom_tool_call') and p.get('name') in ('wait', 'wait_agent'):
            try:
                args = json.loads(p.get('arguments', '{}'))
            except ValueError:
                args = {'unavailable': True}
            waits.append({'timestamp': e['timestamp'], 'tool': p['name'], 'call_id': p.get('call_id'), 'args': args})
    for w in waits:
        raw = str(outputs.get(w['call_id'], ''))
        w['output_length'] = len(raw)
        w['still_running_only'] = 'Script running with cell ID' in raw and raw.rstrip().endswith('Output:')
    for phase in phases.values():
        phase['usd'] = round(phase['usd'], 9)
    return {'worker_start': start, 'worker_end': end,
            'worker_seconds': (datetime.fromisoformat(end.replace('Z', '+00:00')) - datetime.fromisoformat(start.replace('Z', '+00:00'))).total_seconds(),
            'parent_phases': phases, 'wait_calls': waits, 'still_running_only_wait_outputs': sum(w['still_running_only'] for w in waits),
            'note': 'Timestamp bins describe where recorded parent responses occurred. They do not assign causal savings to waits or review.'}


def main():
    root = Path(trial.read(trial.POINTER)['root'])
    prior = trial.read(root / 'postflight-accounting.json')['runs'][0]['agents']
    current = trial.read(root / 'software-recovery-02/accounting.json')['agents']
    report = {}
    for arm, agents in [('native', prior), ('software', current)]:
        parent = next(a for a in agents if a['configurations'] == [['gpt-6-astra', 'high']])
        worker = next(a for a in agents if a['configurations'] == [['gpt-5.6-luna', 'max']])
        report[arm] = analyze(parent, worker)
        print(json.dumps({'arm': arm, **{k:v for k,v in report[arm].items() if k not in ('wait_calls', 'note')},
                          'wait_requests': dict(Counter(json.dumps(w['args'], sort_keys=True) for w in report[arm]['wait_calls']))}))
    trial.save(root / 'software-recovery-02/phase-accounting.json', report)


if __name__ == '__main__':
    main()
