"""Revalidate completed artifacts and run added tests. No model calls or code edits."""
import argparse
import json
from pathlib import Path
import sys

from experiment import BINARY, POINTER, digest, observe, read, runner, save


def main(arm):
    root=Path(read(POINTER)['root']); manifest=read(root/'manifest.json')
    request=root/arm/('repair-request.json' if (root/arm/'result-1.json').exists() else 'request.json')
    job=read(request); task=Path(job['cwd'])
    receipt,handoff=runner.review_gate(job,Path(manifest['state']),str(BINARY))
    added_tests=sorted(task.glob('tests/test_worker*.py'))
    check={'argv':[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_worker*.py','-q'],
           'timeout_seconds':120}
    before=runner.handoff_fingerprints(job,handoff,str(BINARY))
    result=observe(dict(job,profile='review'),check) if added_tests else {'exit_code':0,'stdout':'No added worker tests','stderr':''}
    assert before==runner.handoff_fingerprints(job,handoff,str(BINARY))
    changed=[]
    for path,sha in manifest['frozen'].items():
        p=Path(path)
        if task in p.parents and digest(p)!=sha:
            changed.append(p.relative_to(task).as_posix())
    source={p.relative_to(task).as_posix() for p in task.rglob('*') if p.is_file()
            and '.git' not in p.parts and '__pycache__' not in p.parts}
    initial={Path(p).relative_to(task).as_posix() for p in manifest['frozen'] if task in Path(p).parents}
    added=sorted(source-initial)
    allowed=lambda name: (name.startswith('reservation/') and name.endswith('.py') and name.count('/')==1) or (
        name.startswith('tests/test_worker') and name.endswith('.py') and name.count('/')==1)
    scope_errors=[p for p in [*changed,*added] if not allowed(p)]
    artifact_listing_gaps=[p for p in [*changed,*added] if p not in handoff['artifacts']]
    report={'arm':arm,'checked_id':job['id'],'hashes_unchanged':True,'changed':changed,'added':added,
        'scope_errors':scope_errors,'artifact_listing_gaps':artifact_listing_gaps,'added_test_result':result,
        'handoff':handoff,'manual_source_review':'Required separately; no automatic semantic acceptance.'}
    save(root/arm/'post-review.json',report)
    print(json.dumps(report))
    assert result['exit_code']==0 and not scope_errors and not artifact_listing_gaps


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('arm',choices=['A','B'])
    main(parser.parse_args().arm)
