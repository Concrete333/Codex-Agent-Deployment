"""Revalidate completed pipeline evidence and record separate supervision cost."""
import importlib.util
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'reservation-component'))
from unattended_accounting import snapshot
from unattended import launch_identity
from experiment import read, save


def main():
    root=Path(read(HERE/'local-pipeline.json')['root'])
    plan=read(root/'pipeline-plan.json')
    review=Path(read(root/'pipeline-status.json')['review_root'])
    manifest=read(review/'manifest.json')
    sys.path.insert(0,str(REPO/'scripts'))
    import deployment_runner as runner
    binary=Path.home()/'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
    state=Path(manifest['state'])
    assert not (state/'active.json').exists()
    observations=[]
    for case in manifest['cases']:
        job=read(review/case['label']/'request.json'); task=Path(job['cwd'])
        assert runner.artifact_hashes(job,case['task_sha256'],str(binary))==case['task_sha256']
        assert {p.relative_to(task).as_posix() for p in task.rglob('*') if p.is_file() and '.git' not in p.parts}==set(case['task_sha256'])
        source_job=read(case['original_request'])
        receipt,_=runner.review_gate(source_job,state,str(binary))
        grade=read(receipt['checks'][0]['stdout_path'])
        assert grade['passed'] and grade['methods']==21 and not grade['failures'] and not grade['errors']
        result=read(review/case['label']/'result.json')
        assert result['status']=='completed' and not result['ownership_check_required']
        assert result['report']['decision']=='accept' and not result['report']['findings'] and not result['report']['uncertainties']
        observations.append(dict(arm=case['source_arm'],case=case['label'],grade=grade,hashes_revalidated=True,
                                 reviewer_report=result['report']))
    spec=importlib.util.spec_from_file_location('rates',HERE.parent/'revision-ab/summarize.py')
    rates=importlib.util.module_from_spec(spec); spec.loader.exec_module(rates)
    overhead=dict(setup=snapshot(plan['setup_turn'],rates),current_adjudication_snapshot=snapshot(launch_identity(),rates))
    result=dict(evidence=observations,overhead=overhead,
        limits='No new inference or test execution. Historical API-equivalent rates. Setup is the exact completed launch turn; current adjudication snapshot excludes later/in-flight reporting. Earlier fixture/audit/harness research remains outside this replication subtotal and is not free. Software-only review preparation is not another paid setup turn.')
    save(root/'pipeline-adjudication-accounting.json',result)
    for label,row in overhead.items():
        print(label,{key:row.get(key) for key in ('responses','api_equivalent_usd','completion_event_observed','last_usage_timestamp')})
    print('Both 21-check passes and original/copied artifact hashes revalidated; no active claim.')


if __name__=='__main__': main()
