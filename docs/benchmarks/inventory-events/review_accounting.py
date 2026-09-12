"""Snapshot setup, fixture audit and current acceptance usage; no model calls."""
import importlib.util
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
# Reuse the exact-turn filter from the preceding experiment, not whole-task usage.
sys.path.insert(0,str(HERE.parent/'reservation-component'))
from unattended_accounting import snapshot
from unattended import launch_identity
from experiment import read, save


def main():
    root=Path(read(HERE/'local-fixture.json')['root'])
    manifest=read(root/'manifest.json')
    spec=importlib.util.spec_from_file_location('frozen_rates',HERE.parent/'revision-ab/summarize.py')
    rates=importlib.util.module_from_spec(spec); spec.loader.exec_module(rates)
    current=launch_identity()
    assert current['thread_id']==manifest['setup_turn']['thread_id']
    assert current['turn_id']!=manifest['setup_turn']['turn_id']
    audit_id='01a096c1-6398-74f0-8a2e-68eca2b02320'
    audit_path=Path.home()/'.codex/sessions/2026/09/12'/f'rollout-2026-09-12T18-54-11-{audit_id}.jsonl'
    header=next(rates.entries(audit_path))['payload']
    spawn=header['source']['subagent']['thread_spawn']
    assert header['id']==audit_id and spawn['parent_thread_id']==current['thread_id']
    assert spawn['agent_path']=='/root/audit_inventory_fixture'
    audit=rates.audit_thread(audit_id,dict(path=audit_path,parent=current['thread_id']))
    assert audit['reconciled'] and {tuple(c) for c in audit['configurations']}=={('gpt-5.6-sol','high')}
    result=dict(setup=snapshot(manifest['setup_turn'],rates),fixture_audit=audit,
                acceptance_snapshot=snapshot(current,rates),
                limits='Historical API-equivalent rates, not bills. Current acceptance includes only completed response records through the snapshot, not later reporting/final delivery. Review is shared across arms, not halved. Prior reusable harness research and machine costs excluded.')
    save(root/'review-accounting-snapshot.json',result)
    for label,value in result.items():
        if isinstance(value,dict):
            print(label,{k:value.get(k) for k in ('model','effort','responses','api_equivalent_usd','completion_event_observed','last_usage_timestamp')})


if __name__=='__main__': main()
