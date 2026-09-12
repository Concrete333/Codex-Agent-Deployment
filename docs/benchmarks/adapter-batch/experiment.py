"""Reuse guarded execution/accounting; qualify adapter-specific acceptance first."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import uuid

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('checked_experiment', HERE.parent/'checked-component/experiment.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
shared.HERE = HERE
original_frozen = shared.frozen


def frozen(fixture):
    hashes = original_frozen(fixture)
    paths = [Path(fixture['root'])/'held-out.json', Path(__file__), HERE.parent/'checked-component/experiment.py',
             HERE.parent/'revision-ab/summarize.py']
    paths += [p for p in Path(fixture['reference']).rglob('*') if p.is_file()]
    hashes.update({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    return hashes


shared.frozen = frozen


def preflight(fixture):
    root = Path(fixture['root'])
    assert not (root/'started.json').exists(), 'Cannot preflight again after inference has started'
    destination = root/('preflight-' + uuid.uuid4().hex[:8])
    destination.mkdir(exist_ok=False)
    reference = Path(fixture['reference'])
    mutations = {
        'reference': '',
        'wrong-sign': '\n_original = parse\ndef parse(text):\n    rows = _original(text)\n    for row in rows: row["amount_minor"] = abs(row["amount_minor"])\n    return rows\n',
        'first-only': '\n_original = parse\ndef parse(text):\n    return _original(text)[:1]\n',
        'reverse-order': '\n_original = parse\ndef parse(text):\n    return list(reversed(_original(text)))\n',
        'memo-trim': '\n_original = parse\ndef parse(text):\n    rows = _original(text)\n    for row in rows: row["memo"] = row["memo"].strip()\n    return rows\n',
        'swallow-invalid': '\n_original = parse\ndef parse(text):\n    try: return _original(text)\n    except ValueError: return []\n',
        'checker-tamper': '',
        'stub': '',
    }
    results=[]
    for name, suffix in mutations.items():
        target=destination/name
        shutil.copytree(Path(fixture['source']) if name=='stub' else reference,target)
        if suffix:
            with (target/'imports/adapters/bank_csv.py').open('a',encoding='utf-8') as stream:
                stream.write(suffix)
        if name=='checker-tamper':
            with (target/'check_contract.py').open('a',encoding='utf-8') as stream:
                stream.write('\n# altered\n')
        done=subprocess.run([fixture['python'],'-B','-X','utf8',str(HERE/'grade.py'),str(target)],
                            capture_output=True,text=True,encoding='utf-8',timeout=180)
        shared.save(destination/(name+'.json'),{'exit_code':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
        expected=done.returncode==0 if name=='reference' else done.returncode!=0
        results.append({'case':name,'exit_code':done.returncode,'expected':expected})
        assert expected,name
    binary=Path.home()/'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
    sandbox=subprocess.run([str(binary),'sandbox','-P',':read-only','-C',str(reference),'-c','windows.sandbox="elevated"',
                            '--',fixture['python'],'-B','-X','utf8',str(HERE/'grade.py'),str(reference)],
                           capture_output=True,text=True,encoding='utf-8',timeout=180)
    shared.save(destination/'sandbox.json',{'exit_code':sandbox.returncode,'stdout':sandbox.stdout,'stderr':sandbox.stderr})
    assert sandbox.returncode==0,'Sandbox reference failed'
    for arm in ('A','C'):
        done=subprocess.run(shared.command(fixture,arm,True),cwd=shared.REPO,capture_output=True,text=True,encoding='utf-8',timeout=90)
        shared.save(destination/(arm+'-prompt.json'),{'exit_code':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
        assert done.returncode==0,'Prompt preflight '+arm
    shared.save(root/'preflight.json',{'passed':True,'receipt_directory':str(destination),'mutants':results,'frozen':frozen(fixture)})
    print(json.dumps({'passed':True,'cases':results,'sandbox':sandbox.returncode}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=('preflight','run','summarize'))
    operation=parser.parse_args().operation
    (preflight if operation=='preflight' else getattr(shared,operation))(shared.load())
