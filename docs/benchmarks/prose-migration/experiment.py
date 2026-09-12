"""Reuse the existing runner for exactly one sequential A/C pair.

prepare and summarize are offline. run makes the two explicitly authorized trials.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = HERE.parent / 'pilot/run.py'
LOCAL = HERE / 'local-fixture.json'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def hashes(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}


def prepare():
    if LOCAL.exists():
        raise SystemExit('Fixture already prepared; no automatic regeneration.')
    cases = json.loads((HERE / 'cases.json').read_text(encoding='utf-8'))
    assert [c['id'] for c in cases] == [f'ISSUE-{n:03}' for n in range(1, 51)]
    checker = module('prose_grade', HERE / 'grade.py')
    # mkdir inherits normal Windows permissions; mkdtemp caused prior sandbox access failures.
    root = Path(tempfile.gettempdir()) / ('agent-deployment-prose-' + uuid.uuid4().hex)
    root.mkdir()
    source = root / 'source'
    (source / 'threads').mkdir(parents=True)
    shutil.copy2(HERE / 'TASK.md', source / 'TASK.md')
    answer = {'release': '4.0', 'assessed_at': '2031-06-30', 'records': []}
    for case in cases:
        text = checker.source_text(case)
        (source / 'threads' / (case['id'] + '.md')).write_text(text, encoding='utf-8')
        evidence = []
        for anchor in case['decisive_evidence']:
            assert anchor in text, (case['id'], anchor)
            offset = text.index(anchor)
            start = text[:offset].count('\n') + 1
            evidence.append({'line_start': start, 'line_end': start + anchor.count('\n'), 'quote': anchor})
        answer['records'].append({'id': case['id'], 'disposition': case['expected_disposition'],
                                  'explanation': case['rationale'], 'evidence': evidence})
    reference = root / 'reference'
    shutil.copytree(source, reference)
    save(reference / 'answer.json', answer)
    checked = checker.grade(reference)
    assert checked['automated_pass'], checked
    mutations = {}
    for name in ('missing', 'wrong-decision', 'fake-quote', 'wrong-line', 'unsupported-date'):
        bad = copy.deepcopy(answer)
        if name == 'missing':
            bad['records'].pop()
        elif name == 'wrong-decision':
            bad['records'][0]['disposition'] = 'unresolved' if bad['records'][0]['disposition'] != 'unresolved' else 'required'
        elif name == 'fake-quote':
            bad['records'][0]['evidence'][0]['quote'] = 'This invented sentence never appeared in the source.'
        elif name == 'wrong-line':
            bad['records'][0]['evidence'][0]['line_start'] = 9999
        else:
            bad['assessed_at'] = '2032-01-01'
        save(reference / 'answer.json', bad)
        rejected = checker.grade(reference)
        assert not rejected['automated_pass'], name
        mutations[name] = rejected
    save(reference / 'answer.json', answer)
    original_source = reference / 'threads' / (cases[0]['id'] + '.md')
    original_source.write_text(checker.source_text(cases[0]) + '\nAltered evidence.\n', encoding='utf-8')
    mutations['changed-source'] = checker.grade(reference)
    assert not mutations['changed-source']['automated_pass']
    original_source.write_text(checker.source_text(cases[0]), encoding='utf-8')
    save(root / 'mutant-checks.json', mutations)
    policy = root / 'policy'
    policy.mkdir()
    shutil.copy2(REPO / 'SKILL.md', policy / 'SKILL.md')
    for folder in ('references', 'scripts'):
        shutil.copytree(REPO / folder, policy / folder, ignore=shutil.ignore_patterns('__pycache__'))
    fixture = {'root': str(root), 'source': str(source), 'reference': str(reference),
               'skill_source': str(policy), 'python': sys.executable}
    save(LOCAL, fixture)
    print(json.dumps(dict(fixture, words=sum(len(c['text'].split()) for c in cases),
                          reference=checked, rejected_mutants=len(mutations))))


def run():
    fixture = json.loads(LOCAL.read_text())
    root = Path(fixture['root'])
    plan_path = root / 'run-plan.json'
    if plan_path.exists():
        raise SystemExit('Plan exists: no duplicate trials or automatic retries.')
    # Independent source-only review must be recorded before freezing and launch.
    audit = json.loads((HERE / 'source-audit.json').read_text())
    cases_hash = hashlib.sha256((HERE / 'cases.json').read_bytes()).hexdigest()
    assert audit['cases_sha256'] == cases_hash and audit['approved_for_trial'] is True
    locked = [RUNNER, HERE / 'cases.json', HERE / 'TASK.md', HERE / 'grade.py', Path(__file__), HERE / 'source-audit.json']
    for folder in ('source', 'skill_source'):
        locked.extend(p for p in Path(fixture[folder]).rglob('*') if p.is_file())
    frozen = hashes(locked)
    plan = {'order': ['A', 'C'], 'timeout_seconds': 2700, 'frozen_sha256': frozen, 'runs': []}
    save(plan_path, plan)
    for arm in plan['order']:
        assert hashes(locked) == frozen, 'Frozen inputs changed'
        command = [sys.executable, '-B', '-X', 'utf8', str(RUNNER), arm,
                   '--suite', str(HERE), '--source', fixture['source'], '--python', fixture['python'],
                   '--skill-source', fixture['skill_source'], '--timeout-seconds', '2700']
        if arm == 'C':
            command.append('--allow-claude')
        print(json.dumps({'starting': arm}), flush=True)
        log_path = root / (arm + '.log')
        with log_path.open('w', encoding='utf-8') as log:
            proc = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
        run_path = None
        for line in log_path.read_text(encoding='utf-8').splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if 'prepared' in entry:
                run_path = Path(entry['prepared'])
        result_path = run_path / 'result.json' if run_path else None
        result = json.loads(result_path.read_text()) if result_path and result_path.exists() else None
        row = {'task': 'prose-migration', 'arm': arm, 'runner_exit': proc.returncode,
               'run_directory': str(run_path) if run_path else None, 'result': result}
        plan['runs'].append(row)
        save(plan_path, plan)
        print(json.dumps(row), flush=True)
        if proc.returncode or result is None:
            raise SystemExit('Harness failed; evidence retained; no next paid trial.')
    assert hashes(locked) == frozen, 'Frozen inputs changed during run'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'summarize'])
    mode = parser.parse_args().mode
    if mode == 'summarize':
        summary = module('existing_accounting', HERE.parent / 'revision-ab/summarize.py')
        summary.HERE = HERE
        summary.main()
    elif mode == 'prepare':
        prepare()
    else:
        run()
