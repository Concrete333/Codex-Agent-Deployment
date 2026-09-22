"""Audit the frozen three-arm repeat. No inference or candidate edits."""
import json
import os
from pathlib import Path
import sys

import experiment as trial


def main():
    root = Path(trial.read(trial.HERE / 'local-repeat.json')['root'])
    result, plan = trial.read(root / 'result.json'), trial.read(root / 'run-plan.json')
    assert result['status'] == 'finished'
    receipt = trial.read(root / 'notification/process.json')
    assert receipt['status'] == 'exited' and receipt['exit_code'] == 0
    accounting = trial.module('repeat_accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    accounting.RATES = plan['rates_per_million']
    index = accounting.session_index()
    # Keep the original failed grade intact. UTF-8 fixes reporting only, including
    # the outer grader process on Windows; it does not change cases or candidates.
    os.environ['PYTHONUTF8'] = '1'
    report = {'rates_per_million': accounting.RATES, 'arms': {}, 'cases': plan['cases'],
              'note': 'One run per arm; API-equivalent Codex estimates plus Kilo reported cost. '
                      'Setup, supervision and analysis excluded; not subscription allowance.'}
    for kind in plan['order']:
        arm, state = root / kind, result['arms'][kind]
        manifest = trial.read(arm / 'manifest.json')
        agents = {name: accounting.audit_thread(tid, index[tid]) for name, tid in state['sessions'].items()}
        assert all(a['reconciled'] for a in agents.values())
        assert agents['sol']['configurations'] == [('gpt-5.6-sol', 'high')]
        stages = [('delegated', 'solo')] if kind == 'solo' else [('delegated', 'plan'), ('delegated', 'accept')]
        worker_cost, worker, worker_receipt = 0, None, None
        if kind == 'luna':
            assert agents['luna']['configurations'] == [('gpt-5.6-luna', 'max')]
            stages.append(('worker', 'worker'))
            worker = arm / 'worker/task'
            worker_cost = agents['luna']['api_equivalent_usd']
        elif kind == 'mimo':
            kr = Path(state['kilo_run_dir'])
            worker_receipt, km = trial.read(kr / 'receipt.json'), trial.read(kr / 'manifest.json')
            assert not worker_receipt['ownership_check_required'] and not worker_receipt['termination_unconfirmed']
            assert worker_receipt['exit_code'] == 0 and not Path(km['lock']).exists()
            assert km['steps'] is None and km['model'] == 'kilo/xiaomi/mimo-v2.6-pro' and km['variant'] == 'thinking'
            worker, worker_cost = Path(km['worktree']), worker_receipt['reported_cost']
            assert isinstance(worker_cost, (int, float))
            finishes = [e['part'] for e in trial.jsonl_events(kr / 'events.jsonl') if e['type'] == 'step_finish']
            assert abs(sum(p['cost'] for p in finishes) - worker_cost) < 1e-9
        durations = {}
        for owner, stage in stages:
            proc = trial.read(arm / owner / (stage + '-process.json'))
            assert proc['exit_code'] == 0 and not proc['timed_out'] and not proc['ownership_check_required']
            durations[stage] = proc['duration_seconds']
        final = arm / 'delegated/task'
        assert trial.grade(arm, final, 'final-audit-grade') == 0
        counts = {}
        for check in json.loads(trial.read(arm / 'final-audit-grade.json')['stdout'])['checks']:
            counts[check['check']] = json.loads(check['stdout']) if check['check'] != 'added_tests' else check['stderr']
        worker_grade, changed, changed_from_source = None, [], []
        if worker:
            worker_grade = trial.grade(arm, worker, 'worker-audit-grade')
            for name in manifest['owned']:
                before = (worker / name).read_bytes() if (worker / name).exists() else None
                after = (final / name).read_bytes() if (final / name).exists() else None
                source = (arm / 'source' / name).read_bytes() if (arm / 'source' / name).exists() else None
                if before != after:
                    changed.append(name)
                if before != source:
                    changed_from_source.append(name)
        sol_cost = agents['sol']['api_equivalent_usd']
        plan_cost = 0
        if kind != 'solo':
            usage = next(e['usage'] for e in trial.jsonl_events(arm / 'delegated/plan.stdout') if e['type'] == 'turn.completed')
            cumulative = next(e['usage'] for e in trial.jsonl_events(arm / 'delegated/accept.stdout') if e['type'] == 'turn.completed')
            assert all(agents['sol']['usage'].get(k, 0) == v for k, v in cumulative.items())
            ri, rc, rw, ro = accounting.RATES['gpt-5.6-sol']
            written = usage.get('cache_write_input_tokens', 0)
            assert agents['sol']['max_input'] <= 272000
            plan_cost = ((usage['input_tokens'] - usage['cached_input_tokens'] - written) * ri +
                         usage['cached_input_tokens'] * rc + written * rw + usage['output_tokens'] * ro) / 1e6
        if worker_receipt:
            durations['worker'] = worker_receipt['duration_seconds']
        report['arms'][kind] = {'agents': agents, 'plan_usd': plan_cost, 'worker_usd': worker_cost,
            'solo_or_accept_usd': sol_cost - plan_cost, 'total_usd': sol_cost + worker_cost,
            'stage_seconds': durations, 'model_stage_seconds': sum(durations.values()),
            'final_checks': counts, 'worker_grade_exit_code': worker_grade, 'worker_receipt': worker_receipt,
            'worker_changed_files': changed_from_source, 'acceptance_changed_files': changed}
    baseline = report['arms']['solo']['total_usd']
    for kind, info in report['arms'].items():
        info['saving_percent'] = (1 - info['total_usd'] / baseline) * 100
        print(json.dumps({'arm': kind, **{k: info[k] for k in ('plan_usd', 'worker_usd', 'solo_or_accept_usd',
             'total_usd', 'saving_percent', 'model_stage_seconds', 'worker_grade_exit_code', 'acceptance_changed_files')}}))
    # Audit the reviewer's newly reported correction across all completed
    # submissions and the reference. Keep this separate from frozen scoring.
    probe = '''from imports import parse
text = '<statement currency="USD"><entry id="a" date="2024-02-29" amount="1.00"><memo><![CDATA[literal <!DOCTYPE text]]></memo></entry></statement>'
try:
    print(repr(parse('statement_xml', text)))
except ValueError:
    print('rejected')
'''
    targets = {kind: root / kind / 'delegated/task' for kind in plan['order']}
    targets.update(reference=root / 'reference', luna_before_review=root / 'luna/worker/task')
    report['posthoc_cdata_probe'] = {}
    for name, path in targets.items():
        proc = trial.call([sys.executable, '-B', '-X', 'utf8', '-c', probe], path)
        report['posthoc_cdata_probe'][name] = {'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    print(json.dumps({'posthoc_cdata_probe': report['posthoc_cdata_probe']}))
    trial.save(root / 'accounting.json', report)


if __name__ == '__main__':
    main()
