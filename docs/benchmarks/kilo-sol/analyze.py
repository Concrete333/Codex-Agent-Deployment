"""Recover this pair's usage and grade retained artifacts; no model calls."""
import json
from pathlib import Path
import shutil
import sys

import experiment as trial


def main():
    root = Path(trial.read(trial.POINTER)['root'])
    result = trial.read(root / 'recovery-result.json')
    assert result['status'] == 'finished'
    accounting = trial.module('pair_accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    index = accounting.session_index()
    agents = {arm: accounting.audit_thread(info['thread_id'], index[info['thread_id']])
              for arm, info in result['arms'].items()}
    assert all(a['reconciled'] and a['configurations'] == [('gpt-5.6-sol', 'high')]
               for a in agents.values())
    kilo = Path(result['kilo_run_dir'])
    receipt, manifest = trial.read(kilo / 'receipt.json'), trial.read(kilo / 'manifest.json')
    assert receipt['exit_code'] == 0 and not receipt['ownership_check_required']
    assert not receipt['termination_unconfirmed'] and not Path(manifest['lock']).exists()
    for label in ('plan', 'accept'):
        proc = trial.read(root / 'delegated' / (label + '-process.json'))
        assert proc['exit_code'] == 0 and not proc['ownership_check_required'] and not proc['timed_out']

    # Grade exactly the files integrated by the host, on pristine protected
    # inputs. Preserve the original worktree and its failed byte-hash grade.
    source, candidate = root / 'source', Path(manifest['worktree'])
    protected = list(trial.read(source / 'protected_hashes.json')) + ['protected_hashes.json']
    line_endings = {n: (source / n).read_bytes().replace(b'\r\n', b'\n') ==
                    (candidate / n).read_bytes().replace(b'\r\n', b'\n') for n in protected}
    assert all(line_endings.values()), 'Worker protected change exceeds newline conversion'
    integrated = root / 'worker-regrade'
    shutil.copytree(source, integrated)  # Fresh evidence only, never overwrite.
    owned = trial.read(root / 'manifest.json')['owned']
    for name in owned:
        if (candidate / name).exists():
            shutil.copy2(candidate / name, integrated / name)
    worker_grade = trial.grade(root, integrated, 'worker-integrated-grade')
    final_grades = {arm: trial.grade(root, root / arm / 'task', arm + '-verified-grade')
                    for arm in agents}
    assert all(code == 0 for code in final_grades.values())

    # Same post-hoc counterexample for all submissions; not a held-out score.
    probe = ('from imports import parse\n'
             'text=\'id,date,amount,currency,memo\\na,2024-02-29,1,USD,x"y\\r\\n\'\n'
             'try:\n parse("bank_csv", text)\n'
             'except ValueError:\n print("rejected")\n'
             'else:\n print("accepted")\n')
    probes = {}
    for label, path in [('solo', root / 'solo/task'), ('mimo_before_repair', integrated),
                        ('delegated_final', root / 'delegated/task')]:
        p = trial.call([sys.executable, '-B', '-c', probe], path)
        probes[label] = {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    trial.save(root / 'quote-probe.json', probes)

    phases = {}
    for label in ('plan', 'accept'):
        cumulative = next(e['usage'] for e in trial.jsonl_events(root / 'delegated' / (label + '.stdout'))
                          if e.get('type') == 'turn.completed')
        phases[label] = cumulative
    assert phases['accept'] == agents['delegated']['usage'], 'Resume cumulative usage mismatch'
    phases['accept'] = {k: v - phases['plan'].get(k, 0) for k, v in phases['accept'].items()}
    assert all(v >= 0 for v in phases['accept'].values())
    costs = {}
    for label, u in phases.items():
        costs[label] = ((u['input_tokens'] - u['cached_input_tokens']) * 4 +
                        u['cached_input_tokens'] * .4 + u['output_tokens'] * 20) / 1e6
    baseline = agents['solo']['api_equivalent_usd']
    delegated = agents['delegated']['api_equivalent_usd'] + receipt['reported_cost']
    report = {'agents': agents, 'kilo': receipt, 'stage_usage': phases, 'sol_stage_estimates': costs,
              'solo_usd': baseline, 'delegated_usd': delegated,
              'total_cost_change_percent': (delegated / baseline - 1) * 100,
              'codex_cost_change_percent': (agents['delegated']['api_equivalent_usd'] / baseline - 1) * 100,
              'final_grade_exit_codes': final_grades, 'worker_integrated_grade_exit_code': worker_grade,
              'protected_newline_equivalence': line_endings, 'quote_probe': probes,
              'rates': accounting.RATES['gpt-5.6-sol'],
              'note': 'One recovered pair. API-equivalent Sol estimates plus reported Kilo cost, not allowance. Research setup/recovery excluded.'}
    trial.save(root / 'accounting.json', report)
    print(json.dumps({k: report[k] for k in ('solo_usd', 'delegated_usd', 'total_cost_change_percent',
          'codex_cost_change_percent', 'sol_stage_estimates', 'worker_integrated_grade_exit_code', 'quote_probe')}))


def analyze_followup(kind):
    root = Path(trial.read(trial.HERE / ('local-' + kind + '.json'))['root'])
    result, manifest = trial.read(root / 'result.json'), trial.read(root / 'manifest.json')
    assert result['status'] == 'finished'
    accounting = trial.module('luna_accounting', trial.HERE.parent / 'revision-ab/summarize.py')
    index = accounting.session_index()
    agents = {name: accounting.audit_thread(tid, index[tid]) for name, tid in result['sessions'].items()}
    assert agents['sol']['configurations'] == [('gpt-5.6-sol', 'high')]
    assert all(a['reconciled'] for a in agents.values())
    receipt = None
    stages = [('delegated', 'plan'), ('delegated', 'accept')]
    if kind == 'luna':
        assert agents['luna']['configurations'] == [('gpt-5.6-luna', 'max')]
        candidate = root / 'worker/task'
        stages.append(('worker', 'worker'))
        worker_cost = agents['luna']['api_equivalent_usd']
    else:
        kr = Path(result['kilo_run_dir'])
        receipt, km = trial.read(kr / 'receipt.json'), trial.read(kr / 'manifest.json')
        assert receipt['exit_code'] == 0 and not receipt['ownership_check_required']
        assert not receipt['termination_unconfirmed'] and not Path(km['lock']).exists()
        assert km['steps'] is None and km['model'] == 'kilo/xiaomi/mimo-v2.6-pro' and km['variant'] == 'thinking'
        candidate, worker_cost = Path(km['worktree']), receipt['reported_cost']
        assert isinstance(worker_cost, (int, float))
    for arm, label in stages:
        p = trial.read(root / arm / (label + '-process.json'))
        assert p['exit_code'] == 0 and not p['timed_out'] and not p['ownership_check_required']
    for arm, target in [('worker', candidate), ('delegated', root / 'delegated/task')]:
        assert trial.grade(root, target, arm + '-verified-grade') == 0
    unchanged = {name: (candidate / name).read_bytes() ==
                 (root / 'delegated/task' / name).read_bytes() for name in manifest['owned']
                 if (candidate / name).exists()}
    assert all(unchanged.values())
    probe = ('from imports import parse\n'
             'try:\n parse("bank_csv", \'id,date,amount,currency,memo\\na,2024-02-29,1,USD,x"y\\r\\n\')\n'
             'except ValueError:\n print("rejected")\nelse:\n print("accepted")\n')
    p = trial.call([sys.executable, '-B', '-c', probe], candidate)
    probe_result = {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    ref = trial.call([sys.executable, '-B', '-c', probe], Path(manifest['previous']) / 'reference')
    reference_probe = {'exit_code': ref.returncode, 'stdout': ref.stdout, 'stderr': ref.stderr}
    plan = next(e['usage'] for e in trial.jsonl_events(root / 'delegated/plan.stdout') if e.get('type') == 'turn.completed')
    plan_cost = ((plan['input_tokens'] - plan['cached_input_tokens']) * 4 + plan['cached_input_tokens'] * .4 + plan['output_tokens'] * 20) / 1e6
    total = agents['sol']['api_equivalent_usd'] + worker_cost
    baseline = trial.read(Path(manifest['previous']) / 'accounting.json')['solo_usd']
    report = {'agents': agents, 'worker_receipt': receipt, 'worker_cost': worker_cost,
              'unchanged_worker_files': unchanged, 'quote_probe': probe_result, 'reference_quote_probe': reference_probe,
              'total_usd': total, 'solo_usd': baseline, 'saving_percent': (1 - total / baseline) * 100,
              'plan_usd': plan_cost, 'accept_usd': agents['sol']['api_equivalent_usd'] - plan_cost,
              'note': 'One run; API-equivalent estimates, not subscription usage. Setup/supervision excluded.'}
    trial.save(root / 'accounting.json', report)
    print(json.dumps({k: v for k, v in report.items() if k != 'agents'}))


if __name__ == '__main__':
    if sys.argv[1:] in (['--luna'], ['--uncapped']):
        analyze_followup(sys.argv[1][2:])
    elif not sys.argv[1:]:
        main()
    else:
        raise SystemExit('Usage: analyze.py [--luna|--uncapped]')
