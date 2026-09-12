"""New component A/B. prepare/summary are offline; run spends at most four sessions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'scripts'))
import deployment_runner as runner
import reference

POINTER=HERE/'local-fixture.json'
BINARY=Path.home()/'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
TREATMENT=('Context handling: Discover candidate files within the relevant paths and file types before '
           'reading bodies; exclude unrelated generated or captured content. Read matching functions or '
           'ranges. If output truncates, recover the missing relevant ranges instead of treating the '
           'partial return as complete. Widen the search when evidence or coverage requires it.')
PROTECTED=['SPEC.md','AGENTS.md','tests/test_public.py','reservation/reporting.py']
save=runner.atomic_json
read=runner.read_json


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def observe(job,check):
    p=subprocess.run(runner.build_check(str(BINARY),job,check),cwd=job['cwd'],
                     env=runner.worker_env('codex'),capture_output=True,text=True,
                     encoding='utf-8',timeout=check['timeout_seconds'])
    return dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)


def job_for(root,identity,arm,round_number=0):
    task=root/arm/'task'
    prompt=('Implement SPEC.md in this checkout. Own the reservation component, its callers and focused tests. '
            'Use the existing implementation conventions. The host owns final independent checks. '
            'Read only this checkout; do not inspect evaluator code or sibling attempts. '
            f'For Python commands, use this working interpreter: {sys.executable}.\n')
    if arm=='B': prompt+=TREATMENT+'\n'
    job={'id':f'{identity}-{arm.lower()}-{round_number}', 'provider':'codex',
         'model':'gpt-5.6-luna' if not round_number else 'gpt-5.6-sol',
         'effort':'max' if not round_number else 'high','profile':'edit','cwd':str(task),
         'trusted_context':True,'timeout_seconds':1200 if not round_number else 900,
         'prompt':prompt,'artifacts':['reservation/core.py','reservation/service.py','reservation/api.py'],
         'protected_files':PROTECTED,
         'checks':[{'id':'independent-contract','argv':[sys.executable,'-B',str(HERE/'grade.py'),
              str(task),'--protected',str(root/'protected.json')],'timeout_seconds':120}]}
    return runner.validate(job)


def prepare(supersede_offline=False):
    previous=None
    if POINTER.exists():
        previous=read(POINTER)['root']
        if not supersede_offline or (Path(previous)/'started.json').exists():
            raise ValueError('Existing fixture: preserve it; only unstarted preparations may be explicitly superseded')
    identity='reservation-'+uuid.uuid4().hex[:8]
    root=Path.home()/'AgentDeploymentBenchmarks'/identity
    root.mkdir(parents=True)
    old=read(REPO/'docs/benchmarks/context-scope/local-replication.json')
    state=Path(read(Path(old['root'])/'manifest.json')['state'])
    if (state/'active.json').exists(): raise ValueError('Unresolved shared ownership')
    save(root/'protected.json',{p:digest(HERE/'task'/p) for p in PROTECTED})
    for arm in ['B','A']:
        shutil.copytree(HERE/'task',root/arm/'task',ignore=shutil.ignore_patterns('__pycache__'))
        subprocess.run(['git','init','-q',str(root/arm/'task')],check=True)
        job=job_for(root,identity,arm)
        runner.preflight(str(BINARY),job,runner.worker_env('codex'))
        save(root/arm/'request.json',job)
    # Independently supplied correct implementation plus consequential wrong variants.
    variants={'reference':{},'alias_reference':{'service.py':reference.SERVICE.replace(
        'from .core import reserve_batch','from .core import reserve_batch as reserve').replace(
        'rows = reserve_batch(', 'rows = reserve(').replace("'reserved': reserve_batch(","'reserved': reserve(")},'starter':None,
        'preview_mutates':{'core.py':reference.CORE.replace('if not dry_run:', 'if True:')},
        'duplicate_lost':{'core.py':reference.CORE.replace('totals.get(sku, 0) + count','count')},
        'tenant_mixed':{'core.py':reference.CORE.replace('stock.get((tenant, sku), 0)',"stock.get(('b', sku), 0)")},
        'bool_quantity':{'core.py':reference.CORE.replace('type(count) is not int','not isinstance(count, int)')},
        'journal_alias':{'service.py':reference.SERVICE.replace("deepcopy({'tenant': tenant, 'reserved': rows})","{'tenant': tenant, 'reserved': rows}")},
        'preview_commits':{'api.py':reference.API.replace("return service.preview(request['tenant'], request['lines'])","return service.submit(request['tenant'], request['lines'])")}}
    qualified=[]
    for name,overrides in variants.items():
        target=root/'qualification'/name
        shutil.copytree(HERE/'task',target,ignore=shutil.ignore_patterns('__pycache__'))
        if overrides is not None:
            for filename,code in {'core.py':reference.CORE,'service.py':reference.SERVICE,'api.py':reference.API,**overrides}.items():
                (target/'reservation'/filename).write_text(code,encoding='utf-8')
        job=job_for(root,identity,'A')
        job['cwd']=str(target)
        check=job['checks'][0]
        check['argv']=[str(target) if a==str(root/'A'/'task') else a for a in check['argv']]
        result=observe(job,check)
        save(target.parent/(name+'.json'),result)
        if (result['exit_code']==0)!=(name in ['reference','alias_reference']):
            raise ValueError(f'Qualification failed for {name}: {result}')
        qualified.append({'variant':name,'exit_code':result['exit_code']})
    frozen={}
    for base in [HERE,root/'A',root/'B']:
        for path in base.rglob('*'):
            if path.is_file() and '.git' not in path.parts and '__pycache__' not in path.parts and path!=POINTER:
                frozen[str(path)]=digest(path)
    for path in [root/'protected.json',REPO/'scripts/deployment_runner.py',REPO/'scripts/deployment_hash.py',
                 REPO/'scripts/claude_worker.py',REPO/'docs/benchmarks/revision-ab/summarize.py']:
        frozen[str(path)]=digest(path)
    manifest={'root':str(root),'state':str(state),'identity':identity,'order':['B','A'],
              'frozen':frozen,'qualification':qualified,'maximum_sessions':4,
              'supersedes_unstarted_preparation':previous,
              'correction':'At most one fresh Sol High correction after checks_failed, with identical full failure-log feedback policy.'}
    save(root/'manifest.json',manifest); save(POINTER,{'root':str(root)})
    print(json.dumps({k:manifest[k] for k in ['root','qualification','maximum_sessions']}))


def run():
    root=Path(read(POINTER)['root']); manifest=read(root/'manifest.json')
    for path,sha in manifest['frozen'].items():
        if digest(path)!=sha: raise ValueError('Frozen file changed: '+path)
    with (root/'started.json').open('x') as stream: json.dump({'time':time.time()},stream)
    for arm in manifest['order']:
        job=read(root/arm/'request.json')
        for round_number in [0,1]:
            print(json.dumps({'stage':'starting','arm':arm,'round':round_number,'model':job['model']}),flush=True)
            result=runner.run(job,Path(manifest['state']),str(BINARY))
            save(root/arm/f'result-{round_number}.json',result)
            print(json.dumps({'stage':'finished','arm':arm,'round':round_number,'status':result['status']}),flush=True)
            if result.get('ownership_check_required') or (Path(manifest['state'])/'active.json').exists() or result['status']=='blocked':
                summarize(); return
            if result['status']!='checks_failed' or round_number:
                break
            receipt=read(Path(manifest['state'])/job['id']/'receipt.json')
            check=receipt['checks'][0]
            # Read the complete exact checker output, not selected examples or a new solution.
            feedback=Path(check['stdout_path']).read_text(encoding='utf-8')
            if check.get('stderr_path'): feedback+='\n'+Path(check['stderr_path']).read_text(encoding='utf-8')
            job=job_for(root,manifest['identity'],arm,1)
            job['prompt']+='\nRepair the existing attempt against the unchanged contract. Preserve correct behavior. The prior owner has stopped. Exact independent-check output follows:\n'+feedback
            save(root/arm/'repair-request.json',job)
    summarize()


def summarize():
    root=Path(read(POINTER)['root']); manifest=read(root/'manifest.json')
    spec=importlib.util.spec_from_file_location('accounting',REPO/'docs/benchmarks/revision-ab/summarize.py')
    accounting=importlib.util.module_from_spec(spec); spec.loader.exec_module(accounting)
    index=accounting.session_index(); rows=[]
    for arm in manifest['order']:
        for n,request in [(0,'request.json'),(1,'repair-request.json')]:
            if not (root/arm/f'result-{n}.json').exists(): continue
            job=read(root/arm/request); receipt=read(Path(manifest['state'])/job['id']/'receipt.json')
            tid=receipt.get('worker',{}).get('session_id')
            cost=accounting.audit_thread(tid,index[tid]) if tid in index else {'error':'Missing own-session usage'}
            if cost.get('reconciled'):
                assert cost['configurations']==[(job['model'],job['effort'])]
            row={'arm':arm,'round':n,'status':receipt['status'],'model':job['model'],'effort':job['effort'],
                 'accounting':cost,'checks':receipt.get('checks',[])}
            rows.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ['checks','accounting']}|
                             {'usd':cost.get('api_equivalent_usd'),'usage':cost.get('usage'),'responses':cost.get('responses')}),flush=True)
    save(root/'accounting.json',{'rates':accounting.RATES,'runs':rows,
        'excluded':'Preparation, supervisor conversation, fixture audit and offline grading; API-equivalent estimates not bills.'})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['prepare','run','summarize'])
    parser.add_argument('--supersede-offline',action='store_true')
    args=parser.parse_args()
    if args.operation=='prepare': prepare(args.supersede_offline)
    else: {'run':run,'summarize':summarize}[args.operation]()
