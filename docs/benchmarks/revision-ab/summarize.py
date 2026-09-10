"""Read local trial receipts and reconcile own-thread native usage. No model calls."""
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RATES = {'gpt-6-astra': (10, 1, 12.5, 50), 'gpt-5.6-luna': (.2, .02, .25, 1.2),
         'gpt-5.6-terra': (2, .2, 2.5, 12), 'gpt-5.6-sol': (4, .4, 5, 20)}
FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
          'output_tokens', 'reasoning_output_tokens')


def entries(path):
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def session_index():
    index = {}
    for path in (Path.home() / '.codex/sessions').glob('*/*/*/rollout-*.jsonl'):
        try:
            with path.open(encoding='utf-8') as stream:
                meta = json.loads(next(stream))
            if meta.get('type') != 'session_meta':
                continue
            payload = meta['payload']
            source = payload.get('source')
            parent = source.get('subagent', {}).get('thread_spawn', {}).get('parent_thread_id') if isinstance(source, dict) else None
            index[payload['id']] = {'path': path, 'parent': parent, 'cli_version': payload.get('cli_version')}
        except (OSError, ValueError, StopIteration):
            continue
    return index


def audit_thread(tid, item):
    data = list(entries(item['path']))
    records, contexts = {}, {}
    for entry in data:
        payload = entry.get('payload', {})
        if entry.get('type') == 'turn_context':
            contexts[payload.get('turn_id')] = payload
        if entry.get('type') == 'token_usage_record' and payload.get('thread_id') == tid:
            records[payload['response_id']] = payload
    if not records:
        return {'thread_id': tid, 'error': 'No own-thread response usage found'}
    totals, configurations, tiers = Counter(), set(), set()
    cost, max_input, latest = 0, 0, None
    for record in records.values():
        usage = record['usage']
        context = contexts.get(record['turn_id'], {})
        model, effort = context.get('model'), context.get('effort')
        configurations.add((model, effort))
        tiers.add(context.get('service_tier'))
        totals.update({field: usage.get(field, 0) for field in FIELDS})
        inp, cached, written, out = (usage.get(field, 0) for field in FIELDS[:4])
        uncached = inp - cached - written
        if uncached < 0:
            raise ValueError('Cache counters exceed input: ' + tid)
        if model not in RATES or context.get('service_tier') not in (None, 'default', 'standard'):
            raise ValueError('Unknown pricing configuration: ' + str((model, context.get('service_tier'))))
        ri, rc, rw, ro = RATES[model]
        if inp > 272000:
            ri, rc, rw, ro = ri * 2, rc * 2, rw * 2, ro * 1.5
        cost += (uncached * ri + cached * rc + written * rw + out * ro) / 1e6
        max_input = max(max_input, inp)
        latest = record.get('thread_token_usage')
    own_turns = {record['turn_id'] for record in records.values()}
    calls, wait_calls, spawning = Counter(), [], []
    current = None
    for entry in data:
        payload = entry.get('payload', {})
        if entry.get('type') == 'turn_context':
            current = payload.get('turn_id')
        if current not in own_turns or entry.get('type') != 'response_item':
            continue
        if payload.get('type') not in ('function_call', 'custom_tool_call'):
            continue
        name = payload.get('name', '')
        calls[name] += 1
        if name.endswith(('wait_agent', 'sleep', 'send_message', 'spawn_agent', 'interrupt_agent')):
            raw = payload.get('arguments', '{}')
            try:
                args = json.loads(raw)
            except (ValueError, TypeError):
                args = {}
            compact = {'tool': name, 'timestamp': entry.get('timestamp'),
                       'args': {k: v for k, v in args.items() if k in ('timeout_ms', 'duration_ms', 'model', 'reasoning_effort', 'fork_turns', 'task_name', 'target')}}
            wait_calls.append(compact)
            if name.endswith('spawn_agent'):
                spawning.append(compact)
    reconciled = latest is not None and all(totals[field] == latest.get(field, 0) for field in FIELDS)
    return {'thread_id': tid, 'rollout': str(item['path']), 'parent': item['parent'],
            'configurations': sorted(configurations), 'service_tiers': list(tiers),
            'usage': dict(totals), 'responses': len(records), 'max_input': max_input,
            'api_equivalent_usd': round(cost, 9), 'reconciled': reconciled,
            'tool_calls': dict(calls), 'coordination_calls': wait_calls}


def main():
    fixture = json.loads((HERE / 'local-fixture.json').read_text())
    root = Path(fixture['root'])
    plan = json.loads((root / 'run-plan.json').read_text())
    index = session_index()
    results = []
    for run in plan['runs']:
        tid = (run.get('result') or {}).get('thread_id')
        if tid not in index:
            results.append(dict(run, accounting_error='Root rollout not found'))
            continue
        descendants = {tid}
        while True:
            found = {key for key, item in index.items() if item['parent'] in descendants}
            if found <= descendants:
                break
            descendants.update(found)
        agents = [audit_thread(key, index[key]) for key in sorted(descendants)]
        task = Path(run['run_directory']) / 'task'
        claude = []
        for path in task.rglob('*.json'):
            if not path.parent.name.startswith('claude-worker-receipts-'):
                continue
            try:
                receipt = json.loads(path.read_text(encoding='utf-8'))
            except (ValueError, OSError):
                continue
            if 'requested_model' in receipt and 'estimated_cost_usd' in receipt:
                claude.append({k: receipt.get(k) for k in ('id', 'session_id', 'requested_model', 'requested_effort',
                                                         'status', 'estimated_cost_usd', 'usage', 'model_usage')})
        complete_usage = all(a.get('reconciled') for a in agents) and all(c.get('estimated_cost_usd') is not None for c in claude)
        total = sum(a.get('api_equivalent_usd', 0) for a in agents) + sum(c.get('estimated_cost_usd') or 0 for c in claude)
        offline_path = Path(run['run_directory']) / 'offline-regrade.json'
        offline = json.loads(offline_path.read_text(encoding='utf-8')) if offline_path.is_file() else None
        acceptance = offline['grade_exit_code'] if offline else run['result']['grade_exit_code']
        results.append(dict(run, agents=agents, claude=claude, accounting_reconciled=complete_usage,
                            acceptance_exit_code=acceptance, offline_regrade_used=bool(offline),
                            captured_api_equivalent_usd=round(total, 9)))
    report = {'rates_per_million': RATES, 'runs': results,
              'note': 'API-equivalent estimates, not allowance; setup/supervision/evaluation excluded. Timeouts may omit in-flight usage.'}
    (root / 'accounting.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    for result in results:
        print(json.dumps({k: result.get(k) for k in ('task', 'arm', 'captured_api_equivalent_usd', 'accounting_reconciled', 'accounting_error')}))


if __name__ == '__main__':
    main()
