"""Fresh repeat of the qualified reservation pair; preserve original identities."""
import argparse
import json
from pathlib import Path

import experiment as base

ORIGINAL=base.POINTER
POINTER=base.HERE/'local-repeat.json'


def prepare():
    if POINTER.exists(): raise ValueError('Repeat already prepared; do not overwrite')
    old_root=Path(base.read(ORIGINAL)['root'])
    old=base.read(old_root/'manifest.json')
    # Verify participant/evaluator/runtime bytes, not public result documents
    # that were legitimately written after the original trial finished.
    required=[base.HERE/name for name in ['experiment.py','grade.py','reference.py']]
    required.extend(p for p in (base.HERE/'task').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    required.extend(base.REPO/name for name in ['scripts/deployment_runner.py','scripts/deployment_hash.py',
                    'scripts/claude_worker.py','docs/benchmarks/revision-ab/summarize.py'])
    for path in required:
        if base.digest(path)!=old['frozen'].get(str(path)):
            raise ValueError('Original frozen component/runtime changed: '+str(path))
    base.POINTER=POINTER
    base.prepare()
    root=Path(base.read(POINTER)['root']); current=base.read(root/'manifest.json')
    if current['state']!=old['state'] or current['order']!=old['order']:
        raise ValueError('State or order changed')
    for arm in current['order']:
        before=base.read(old_root/arm/'request.json'); after=base.read(root/arm/'request.json')
        before['id']=after['id']='CELL'
        if json.dumps(before,sort_keys=True).replace(str(old_root).replace('\\','\\\\'),'ROOT') != \
           json.dumps(after,sort_keys=True).replace(str(root).replace('\\','\\\\'),'ROOT'):
            raise ValueError('Assignment configuration changed for '+arm)
    current['repeat_of']=str(old_root)
    current['equivalence']='Original source, evaluator, runner and accounting hashes matched; requests differ only in identity and private paths.'
    base.save(root/'manifest.json',current)
    print(json.dumps({'root':str(root),'repeat_of':str(old_root),'equivalence':current['equivalence']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['prepare','run','summarize','review','metrics'])
    parser.add_argument('--arm',choices=['A','B'])
    args=parser.parse_args()
    if args.operation=='prepare': prepare()
    else:
        base.POINTER=POINTER
        if args.operation in ['run','summarize']:
            {'run':base.run,'summarize':base.summarize}[args.operation]()
        elif args.operation=='review':
            if not args.arm: parser.error('--arm required for review')
            import review_saved
            review_saved.POINTER=POINTER
            review_saved.main(args.arm)
        else:
            import trace_metrics
            trace_metrics.POINTER=POINTER
            trace_metrics.main()
