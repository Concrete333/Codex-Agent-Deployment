"""Recover partial accounting after a harness failure; never launch a model or edit a trial."""
import importlib.util
import json
from pathlib import Path
import sys

import experiment as trial


def main():
    root = Path(trial.read(trial.POINTER)['root'])
    fixture = trial.read(root / 'manifest.json')
    assert fixture['frozen'] == trial.tracked_files(fixture), 'Frozen inputs changed'
    spec = importlib.util.spec_from_file_location('accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    index = accounting.session_index()
    rows = []
    for arm in fixture['order']:
        folder = root / arm
        events = [json.loads(line) for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
        tid = next(e['thread_id'] for e in events if e['type'] == 'thread.started')
        tids = {tid}
        worker_receipt = Path(fixture['state']) / ('adapter-' + arm) / 'receipt.json'
        if worker_receipt.exists():
            tids.add(trial.read(worker_receipt)['worker']['session_id'])
        while True:
            children = {key for key, meta in index.items() if meta['parent'] in tids}
            if children <= tids:
                break
            tids |= children
        agents = [accounting.audit_thread(key, index[key]) for key in sorted(tids)]
        assert all(a.get('reconciled') for a in agents)
        row = {'arm': arm, 'thread_id': tid, 'agents': agents,
               'api_equivalent_usd': sum(a['api_equivalent_usd'] for a in agents),
               'final_messages': [e['item']['text'] for e in events if e['type'] == 'item.completed'
                                  and e['item']['type'] == 'agent_message'][-1:],
               'launch_errors': [e['item'] for e in events if e['type'] == 'item.completed'
                                 and e['item']['type'] == 'command_execution' and e['item']['exit_code'] != 0],
               'result': trial.read(folder / 'result.json') if (folder / 'result.json').exists() else None}
        if arm == 'software':
            row['grade'] = trial.observed(trial.sandbox(folder / 'task', [sys.executable, '-B', '-X', 'utf8',
                str(trial.SUITE / 'grade.py'), str(folder / 'task')]), folder, 'postflight-grade')
            row['worker_attempt_directory_exists'] = (Path(fixture['state']) / 'adapter-software').exists()
            row['dispatch_record_exists'] = (Path(fixture['state']) / '.host-tickets/adapter-software/dispatch.json').exists()
            row['active_claim_exists'] = (Path(fixture['state']) / 'active.json').exists()
            probes = {}
            for name, script in [('copied', Path(fixture['policy']) / 'scripts/deployment_host.py'),
                                 ('canonical', trial.REPO / 'scripts/deployment_host.py')]:
                cmd = trial.sandbox(folder / 'task', [sys.executable, '-B', '-X', 'utf8', str(script), '--help'])
                cmd[cmd.index(':read-only')] = ':workspace'
                probes[name] = trial.observed(cmd, folder, 'postflight-script-' + name)
            row['script_access_probes'] = probes
            row['script_bytes_identical'] = trial.sha(Path(fixture['policy']) / 'scripts/deployment_host.py') == trial.sha(trial.REPO / 'scripts/deployment_host.py')
        rows.append(row)
        print(json.dumps({'arm': arm, 'api_equivalent_usd': row['api_equivalent_usd'], 'agents': len(agents)}))
    trial.save(root / 'postflight-accounting.json', {'runs': rows, 'rates_per_million': accounting.RATES,
        'note': 'Partial pair: software failed before worker launch. No saving established. Research setup/supervision and external evaluation excluded; not allowance.'})


if __name__ == '__main__':
    main()
