"""Verify saved review evidence and snapshot research overhead; no inference or tests."""
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'reservation-component'))
from unattended_accounting import snapshot
from unattended import launch_identity
from experiment import read, save


def main():
    root=Path(read(HERE/'local-acceptance.json')['root']); manifest=read(root/'manifest.json')
    original=Path(manifest['original'])
    sys.path.insert(0,str(REPO/'scripts'))
    import deployment_runner as runner
    binary=Path.home()/'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
    if (Path(manifest['state'])/'active.json').exists(): raise ValueError('Ownership remains active')
    observations=[]
    for case in manifest['cases']:
        job=read(root/case['label']/'request.json')
        actual=runner.artifact_hashes(job,case['task_sha256'],str(binary))
        assert actual==case['task_sha256']
        task=Path(job['cwd'])
        actual_names={p.relative_to(task).as_posix() for p in task.rglob('*') if p.is_file() and '.git' not in p.parts}
        assert actual_names==set(case['task_sha256'])
        runner.review_gate(read(case['original_request']),Path(manifest['state']),str(binary))
        result=read(root/case['label']/'result.json')
        assert result['status']=='completed' and not result['ownership_check_required']
        assert result['report']['decision']=='accept' and not result['report']['findings'] and not result['report']['uncertainties']
        observations.append(dict(case=case['label'],source_arm=case['source_arm'],hashes_revalidated=True,
                                 reported_coverage=result['report']['coverage']))
    spec=importlib.util.spec_from_file_location('rates',HERE.parent/'revision-ab/summarize.py')
    rates=importlib.util.module_from_spec(spec); spec.loader.exec_module(rates)
    prior=read(original/'review-accounting-snapshot.json')
    result=dict(evidence=observations,
        original_setup=snapshot(prior['setup'],rates),
        fixture_audit=prior['fixture_audit'],
        previous_joint_review=snapshot(prior['acceptance_snapshot'],rates),
        separate_review_setup=snapshot(manifest['setup_turn'],rates),
        current_adjudication_snapshot=snapshot(launch_identity(),rates),
        limits='Historical API-equivalent rates. Prior joint review is sunk research, not added to both per-arm costs. Current turn excludes subsequent/in-flight usage. Prior general harness research, intervening planning-only turns and machine costs not included.')
    save(root/'adjudication-accounting.json',result)
    for label in ('original_setup','fixture_audit','previous_joint_review','separate_review_setup','current_adjudication_snapshot'):
        row=result[label]
        print(label,{key:row.get(key) for key in ('responses','api_equivalent_usd','completion_event_observed','last_usage_timestamp')})
    print('Both reviewer copies and original checked submissions unchanged; ownership clear.')


if __name__=='__main__': main()
