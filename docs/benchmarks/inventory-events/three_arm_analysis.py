"""Offline receipt, artifact and usage audit of the fresh inventory comparison."""
import json
from pathlib import Path

import three_arm as trial


def main():
    root = Path(trial.read(trial.POINTER)['root'])
    m, result = trial.read(root/'manifest.json'), trial.read(root/'result.json')
    assert result['status'] == 'finished'
    process = trial.read(root/'notification/process.json')
    assert process['status'] == 'exited' and process['exit_code'] == 0
    accounting = trial.pair.module('inventory_accounting', trial.HERE.parent/'revision-ab/summarize.py')
    accounting.RATES = m['rates_per_million']
    index = accounting.session_index()
    report = {'rates': accounting.RATES, 'arms': {}, 'note': 'One run per condition. '
        'API-equivalent estimates, not allowance. Research setup and analysis excluded.'}
    for kind in m['order']:
        arm, state = root/kind, result['arms'][kind]
        assert state['status'] == 'finished' and state['qualified']
        agents = {name: accounting.audit_thread(tid, index[tid]) for name, tid in state['sessions'].items()}
        assert all(a['reconciled'] for a in agents.values())
        assert agents['astra']['configurations'] == [('gpt-6-astra', 'high')]
        stages = [('delegated', 'implement' if kind == 'solo' else 'accept')]
        worker, worker_cost, worker_receipt, gap = None, 0, None, None
        if kind == 'luna':
            assert agents['luna']['configurations'] == [('gpt-5.6-luna', 'max')]
            stages.append(('worker', 'implement'))
            worker = arm/'worker/task'
            worker_cost = agents['luna']['api_equivalent_usd']
        elif kind == 'mimo':
            kr = Path(state['kilo_run_dir'])
            worker_receipt, km = trial.read(kr/'receipt.json'), trial.read(kr/'manifest.json')
            assert not worker_receipt['ownership_check_required'] and not worker_receipt['termination_unconfirmed']
            assert not Path(km['lock']).exists() and worker_receipt['exit_code'] is not None
            assert km['steps'] is None and km['model'] == 'kilo/xiaomi/mimo-v2.6-pro' and km['variant'] == 'thinking'
            worker, worker_cost = Path(km['worktree']), worker_receipt['reported_cost']
            events = trial.pair.jsonl_events(kr/'events.jsonl')
            finishes = {e['part']['id']: e['part'] for e in events if e['type'] == 'step_finish'}
            assert abs(sum(p['cost'] for p in finishes.values()) - worker_cost) < 1e-9
            errors = [e for e in events if e['type'] == 'error']
            if errors:
                gap = {'reason': 'Failed provider request lacks completed usage; captured cost may be incomplete', 'errors': errors}
        durations = {}
        for owner, label in stages:
            proc = trial.read(arm/owner/(label+'-process.json'))
            assert proc['exit_code'] == 0 and not proc['timed_out'] and not proc['ownership_check_required']
            durations[owner+'-'+label] = proc['duration_seconds']
        if worker_receipt:
            durations['worker'] = worker_receipt['duration_seconds']
        final = arm/'delegated/task'
        grade = trial.grade(root, final, kind+'-audit-final')
        assert grade['passed']
        changed, worker_changed = [], []
        worker_grade = None
        if worker:
            worker_grade = trial.grade(root, worker, kind+'-audit-worker')['passed']
            candidates = {p.relative_to(base).as_posix() for base in (worker, final) for p in base.rglob('*.py')
                          if '__pycache__' not in p.parts and '.git' not in p.parts}
            for name in sorted(candidates):
                before = trial.sha(worker/name) if (worker/name).is_file() else None
                after = trial.sha(final/name) if (final/name).is_file() else None
                original = trial.sha(root/'source'/name) if (root/'source'/name).is_file() else None
                if before != after:
                    changed.append(name)
                if before != original:
                    worker_changed.append(name)
        total = agents['astra']['api_equivalent_usd'] + worker_cost
        report['arms'][kind] = {'agents': agents, 'worker_receipt': worker_receipt, 'worker_usd': worker_cost,
            'astra_usd': agents['astra']['api_equivalent_usd'], 'captured_total_usd': total, 'cost_gap': gap,
            'final_grade': json.loads(grade['stdout']), 'added_tests': grade['added'], 'worker_passed': worker_grade,
            'worker_changed_files': worker_changed, 'acceptance_changed_files': changed,
            'stage_seconds': durations, 'elapsed_seconds': state['finished_at']-state['started_at'],
            'final_file_hashes': {p.relative_to(final).as_posix(): trial.sha(p) for p in final.rglob('*.py')
                                 if '__pycache__' not in p.parts}}
    baseline = report['arms']['solo']['captured_total_usd']
    for kind, info in report['arms'].items():
        info['captured_change_percent'] = (info['captured_total_usd']/baseline-1)*100
        print(json.dumps({'arm': kind, **{k: info[k] for k in ('astra_usd', 'worker_usd', 'captured_total_usd',
            'captured_change_percent', 'elapsed_seconds', 'worker_passed', 'acceptance_changed_files', 'cost_gap')}}))
    trial.save(root/'accounting.json', report)


if __name__ == '__main__':
    main()
