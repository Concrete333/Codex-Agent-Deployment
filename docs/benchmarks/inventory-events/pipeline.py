"""Fresh implementations followed automatically by the frozen separate-review pair."""
import argparse
import json
import os
from pathlib import Path
import time

import experiment as implementation
import acceptance_pair as acceptance

HERE=Path(__file__).resolve().parent
POINTER=HERE/'local-pipeline.json'
read,save=implementation.read,implementation.save


def report(root,phase,error=None,review_root=None):
    value=dict(phase=phase,accepted=False,error=error,review_root=str(review_root) if review_root else None,
               updated_at_unix=time.time())
    save(root/'pipeline-status.json',value)
    (root/'PIPELINE-STATUS.md').write_text('# Fresh inventory pipeline replication\n\n'
        f'Status: **{phase}**\n\n'
        'Astra High solo and Luna Max implementations, then separate read-only Astra High reviews.\n'
        'Maximum four inference sessions; no retry, repair or model polling.\n'
        'Return to the original task when completed_for_adjudication or needs_attention.\n'
        +(f'\nError: {error}\n' if error else ''),encoding='utf-8')


def prepare():
    if POINTER.exists(): raise ValueError('Existing pipeline preparation must be preserved')
    old_root=Path(read(implementation.POINTER)['root'])
    old_manifest=read(old_root/'manifest.json')
    old_review=Path(read(acceptance.POINTER)['root'])
    review_manifest=read(old_review/'manifest.json')
    # Ignore historical reporting edits; pin every task/checker and execution input.
    pinned={p:sha for p,sha in old_manifest['frozen'].items()
            if Path(p).is_relative_to(HERE/'task') or Path(p) in [HERE/'grade.py',HERE/'reference.py',HERE/'experiment.py']
            or Path(p).parent==implementation.REPO/'scripts'
            or Path(p)==HERE.parent/'revision-ab/summarize.py'}
    pinned.update(review_manifest['frozen'])
    if any(implementation.sha(p)!=sha for p,sha in pinned.items()): raise ValueError('Original executable inputs changed')
    implementation.POINTER=POINTER
    implementation.prepare()  # Same qualification and sandbox preflights, fresh stubs only.
    root=Path(read(POINTER)['root'])
    for arm in ['solo','worker']:
        old=read(old_root/arm/'request.json'); new=read(root/arm/'request.json')
        normalized=json.loads(json.dumps(new).replace(str(root).replace('\\','\\\\'),str(old_root).replace('\\','\\\\')))
        normalized['id']=old['id']
        if normalized!=old: raise ValueError('Implementation request differs beyond identity/path')
    plan=dict(root=str(root),original_implementation=str(old_root),original_reviews=str(old_review),
        maximum_inference_sessions=4,automatic_retry=False,
        setup_turn=read(root/'manifest.json')['setup_turn'],
        pinned=pinned | {str(Path(__file__)):implementation.sha(Path(__file__)),
                         str(HERE/'pipeline-protocol.md'):implementation.sha(HERE/'pipeline-protocol.md')},
        authorization='User approved the next full-sequence benchmark after the separate acceptance comparison. Two benchmark-only Astra High review sessions; no operational allowlist change.')
    save(root/'pipeline-plan.json',plan)
    report(root,'prepared')
    print(json.dumps(dict(root=str(root),maximum_sessions=4,inputs_match_original=True)))


def run():
    root=Path(read(POINTER)['root']); plan=read(root/'pipeline-plan.json')
    if any(implementation.sha(p)!=sha for p,sha in plan['pinned'].items()): raise ValueError('Pinned pipeline input changed')
    with (root/'pipeline-started.json').open('x') as stream:
        json.dump(dict(pid=os.getpid(),time=time.time()),stream)
    review_root=None
    try:
        implementation.POINTER=POINTER
        report(root,'implementations_running')
        implementation.run()
        if read(root/'batch-status.json')['status']!='ready_for_review':
            raise RuntimeError('An implementation did not qualify; no paid acceptance or automatic repair')
        report(root,'preparing_read_only_reviews')
        acceptance.POINTER=root/'review-pointer.json'
        acceptance.prepare()
        review_root=Path(read(acceptance.POINTER)['root'])
        # Review prompts must match the original byte-for-byte, not just model/effort.
        old=Path(plan['original_reviews'])
        exemplar=read(old/'case-1/request.json')
        for label in ['case-1','case-2']:
            job=read(review_root/label/'request.json')
            for key in ('prompt','provider','model','effort','profile','timeout_seconds','artifacts','checks'):
                if job[key]!=exemplar[key]: raise ValueError('Review configuration drift: '+key)
        report(root,'reviews_running',review_root=review_root)
        acceptance.run()
        if read(review_root/'batch-status.json')['status']!='completed': raise RuntimeError('Reviews incomplete')
        accounting=read(review_root/'accounting.json')
        accounting['limits']=('Fresh implementation and separate review executed in one uninterrupted host batch. '
            'Per-arm figures include both measured sessions, not setup/research or later adjudication. '
            'No retries/corrections. Historical API-equivalent rates, not bills. Review decisions require adjudication.')
        save(root/'pipeline-accounting.json',accounting)
        report(root,'completed_for_adjudication',review_root=review_root)
    except BaseException as exc:
        report(root,'needs_attention',str(exc),review_root)
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('operation',choices=['prepare','run'])
    args=parser.parse_args(); globals()[args.operation]()
