"""Prepare isolated task, reference, cases and frozen runner without inference."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
from make_cases import build, FORMATS

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def main():
    local = HERE/'local-fixture.json'
    if local.exists():
        raise SystemExit('Prepared fixture exists; preserve earlier identities.')
    for fmt in FORMATS:
        assert (HERE/'reference'/f'{fmt}.py').is_file(), fmt
        assert 'NotImplementedError' in (HERE/'task/imports/adapters'/f'{fmt}.py').read_text(encoding='utf-8')
    root = Path(tempfile.gettempdir())/('agent-deployment-adapters-'+uuid.uuid4().hex)
    root.mkdir()
    source = root/'source'
    shutil.copytree(HERE/'task', source, ignore=shutil.ignore_patterns('__pycache__'))
    save(source/'fixtures.json', build())
    save(root/'held-out.json', build(hidden=True))
    owned = {f'imports/adapters/{fmt}.py' for fmt in FORMATS}
    save(source/'protected_hashes.json', {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(source.rglob('*')) if p.is_file() and p.relative_to(source).as_posix() not in owned})
    reference = root/'reference'
    shutil.copytree(source, reference)
    for file in (HERE/'reference').glob('*.py'):
        shutil.copy2(file, reference/'imports/adapters'/file.name)
    policy = root/'policy'
    policy.mkdir()
    shutil.copy2(REPO/'SKILL.md', policy/'SKILL.md')
    shutil.copytree(REPO/'references', policy/'references')
    runner = (HERE.parent/'pilot/run.py').read_text(encoding='utf-8')
    runner = runner.replace("'agents.max_concurrent_threads_per_session': 2", "'agents.max_concurrent_threads_per_session': 1")
    runner = runner.replace('at most two active children', 'at most one active child')
    runner = runner.replace("'Available worker models: gpt-5.6-luna, gpt-5.6-terra, gpt-5.6-sol'", "'Available worker model: gpt-5.6-luna'")
    runner = runner.replace("+ ('' if args.allow_claude else ', gpt-6-astra') + '; '", "+ '; '")
    runner = runner.replace("'efforts: low, medium, high, xhigh, max. '", "'effort: max only. '")
    marker = "    (run / 'prompt.txt').write_text(prompt, encoding='utf-8')"
    directive = ('Required execution: use the supplied skill and delegate the complete adapter batch to exactly one '
                 'gpt-5.6-luna worker at max effort with fork_turns="none". The worker owns implementation, '
                 'local checks and corrections. Retain final acceptance. Do not launch other workers or nested delegates.')
    assert runner.count(marker)==1
    runner = runner.replace(marker, "    if args.arm == 'C':\n        prompt += " + repr('\n'+directive+'\n') + '\n' + marker)
    (root/'run.py').write_text(runner, encoding='utf-8')
    save(local, {'root':str(root),'source':str(source),'reference':str(reference),'policy':str(policy),
                 'runner':str(root/'run.py'),'python':sys.executable,'formats':list(FORMATS)})
    print(json.dumps({'prepared':str(root),'public_cases':len(build()),'held_out_cases':len(build(True)),
                      'forced_directive_words':len(directive.split())}))


if __name__=='__main__':
    main()
