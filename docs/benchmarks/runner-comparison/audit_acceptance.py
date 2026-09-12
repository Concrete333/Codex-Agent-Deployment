"""Offline postflight: final hashes, protected files and identical new probes on saved arms."""
import json
import argparse
from pathlib import Path
import sys

import recover_acceptance as recovery

trial = recovery.trial


def main(attempt='02'):
    root, folder, job, old, target = recovery.inputs()
    if attempt == '03':
        recovery.pipeline.ARM = 'host-pipeline-03'
        root, folder, job, old, _ = recovery.inputs()
        target = folder
    original = trial.read(old / 'receipt.json')
    assert original['protected_sha256'] == trial.runner.protected_hashes(job)
    handoff = trial.read(old / 'handoff.json')
    test_name = 'test_csv_quoting.py' if attempt == '03' else 'test_review_regressions.py'
    names = handoff['artifacts'] + [test_name]
    final = trial.runner.artifact_hashes(job, names, str(trial.BINARY))
    before = trial.read((old if attempt == '03' else target) / 'receipt.json')['handoff_artifact_sha256']
    changed = [name for name, digest in before.items() if final[name] != digest]
    test = str(Path(job['cwd']) / test_name)
    code = "import runpy,sys; sys.path.insert(0,sys.argv[1]); test=sys.argv[2]; sys.argv=[test]; runpy.run_path(test,run_name='__main__')"
    controls = {}
    for arm, task in [('native', root / 'native/task'),
                      ('software-recovery-02', root / 'software-recovery-02/task'),
                      ('reference', Path(trial.read(trial.SUITE / 'local-fixture.json')['reference'])),
                      ('host-pipeline-' + attempt, Path(job['cwd']))]:
        controls[arm] = trial.observed(trial.sandbox(task, [sys.executable, '-B', '-X', 'utf8',
              '-c', code, str(task), test]), target, 'posthoc-regressions-' + arm)
    events = [json.loads(line) for line in (target / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
    failing = [e['item']['aggregated_output'] for e in events if e.get('type') == 'item.completed'
               and e['item'].get('type') == 'command_execution'
               and e['item'].get('exit_code') != 0
               and 'FAILED (' in e['item'].get('aggregated_output', '')]
    report = {'protected_files_checked': len(original['protected_sha256']), 'protected_files_unchanged': True,
              'final_sha256': final, 'changed_worker_artifacts': changed,
              'pre_correction_failure_evidence': failing,
              'posthoc_controls': controls, 'paid_calls': 0,
              'note': 'Post-hoc reviewer-written probes, not frozen or held-out validation. Saved baseline implementations unmodified.'}
    trial.save(target / 'postflight.json', report)
    print(json.dumps({'changed_worker_artifacts': changed, 'protected_files_checked': report['protected_files_checked'],
                      'posthoc_exit_codes': {arm: item['exit_code'] for arm, item in controls.items()}}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', choices=('02', '03'), default='02')
    main(parser.parse_args().attempt)
