"""Fresh three-arm repeat with clarified CSV grammar and frozen accounting."""
import argparse
import json
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import time
import uuid

import experiment as pair
import luna
import uncapped
from make_cases import record, csv_text

HERE = Path(__file__).resolve().parent
POINTER = HERE / 'local-repeat.json'
read, save = pair.read, pair.save


def quote_cases(hidden=False):
    cases = []
    for fmt, sep, header, row in [
        ('bank_csv', ',', ['id', 'date', 'amount', 'currency', 'memo'], ['a', '2024-02-29', '1.00', 'USD', '']),
        ('euro_csv', ';', ['reference', 'booked', 'debit', 'credit', 'ccy', 'description'], ['a', '29/02/2024', '', '1,00', 'USD', ''])]:
        bad = row.copy()
        bad[-1] = 'prefix"mid"suffix' if hidden else 'x"y'
        cases.append({'name': fmt + '/bare-quote-memo', 'format': fmt,
                      'text': sep.join(header) + '\r\n' + sep.join(bad) + '\r\n', 'error': True})
        good = row.copy()
        good[-1] = 'line 1\n"line 2"' if hidden else 'x"y'
        cases.append({'name': fmt + '/escaped-quote-control', 'format': fmt,
                      'text': csv_text([header, good], sep), 'expected': [record(minor=100, memo=good[-1])]})
        if hidden:
            bad = row.copy()
            bad[0], bad[-1] = 'a"b', 'memo'
            cases.append({'name': fmt + '/bare-quote-id', 'format': fmt,
                          'text': sep.join(header) + '\n' + sep.join(bad), 'error': True})
    return cases


def prepare():
    assert not POINTER.exists(), 'Existing repeat must be preserved'
    previous = Path(read(pair.POINTER)['root'])
    old = read(previous / 'manifest.json')
    root = Path(tempfile.gettempdir()) / ('deployment-repeat-' + uuid.uuid4().hex)
    root.mkdir()
    source = root / 'source'
    shutil.copytree(previous / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    for p in source.rglob('*'):
        if p.is_file():
            assert pair.sha(p) == old['frozen'][str(previous / 'source' / p.relative_to(source))]
    rule = ('Malformed CSV quoting is invalid. A double quote may appear only at the start of a quoted '
            'field or as an escaped doubled quote inside that field. Any double quote in an unquoted '
            'field is invalid, including IDs and memos. For example, unquoted x"y is invalid, while '
            'the quoted field "x""y" is valid and decodes to x"y. After a closing quote, only a delimiter, '
            'record separator or end of input is valid. These rules also apply to euro_csv.')
    task = source / 'TASK.md'
    text = task.read_text(encoding='utf-8')
    assert text.count('Malformed CSV quoting is invalid.') == 1
    task.write_text(text.replace('Malformed CSV quoting is invalid.', rule), encoding='utf-8')
    save(source / 'fixtures.json', read(source / 'fixtures.json') + quote_cases())
    save(root / 'held-out.json', read(previous / 'held-out.json') + quote_cases(True))
    protected = read(source / 'protected_hashes.json')
    save(source / 'protected_hashes.json', {name: pair.sha(source / name) for name in protected})
    save(root / 'local-fixture.json', {'root': str(root), 'source': str(source), 'formats': old['formats']})
    reference = root / 'reference'
    shutil.copytree(source, reference)
    for p in (previous / 'reference/imports/adapters').glob('*.py'):
        shutil.copy2(p, reference / 'imports/adapters' / p.name)
    assert pair.grade(root, reference, 'qualification-reference') == 0
    assert pair.grade(root, source, 'qualification-stubs') != 0
    mutant = root / 'permissive-csv-mutant'
    shutil.copytree(reference, mutant)
    for name in ('bank_csv.py', 'euro_csv.py'):
        p = mutant / 'imports/adapters' / name
        p.write_text(p.read_text().replace('reader = _shared.reader(', 'reader = csv.reader('), encoding='utf-8')
    assert pair.grade(root, mutant, 'qualification-quotes') != 0
    checks = json.loads(read(root / 'qualification-quotes.json')['stdout'])['checks']
    failures = json.loads(next(c['stdout'] for c in checks if c['check'] == 'public'))['failures']
    assert {f['case'] for f in failures} >= {'bank_csv/bare-quote-memo', 'euro_csv/bare-quote-memo'}
    common = (previous / 'solo-prompt.txt').read_text().split('Do all implementation and verification yourself.')[0]
    accounting = pair.module('repeat_rates', HERE.parent / 'revision-ab/summarize.py')
    shared_scripts = [Path(__file__), Path(pair.__file__), Path(luna.__file__), Path(uncapped.__file__),
        pair.BASE / 'grade.py', HERE.parent / 'revision-ab/summarize.py', pair.REPO / 'scripts/deployment_runner.py',
        pair.REPO / 'scripts/claude_worker.py', pair.KILO / 'scripts/kilo_delegate.py', pair.KILO / 'settings.json']
    order = ['solo', 'luna', 'mimo']
    random.Random(20260922).shuffle(order)
    for kind in order:
        arm = root / kind
        shutil.copytree(source, arm / 'source')
        shutil.copy2(root / 'held-out.json', arm / 'held-out.json')
        save(arm / 'local-fixture.json', {'root': str(arm), 'source': str(arm / 'source'), 'formats': old['formats']})
        for owner in (['delegated', 'worker'] if kind == 'luna' else ['delegated']):
            checkout = arm / owner / 'task'
            shutil.copytree(source, checkout)
            for argv in (['git', 'init', '-q'], ['git', 'config', 'core.autocrlf', 'false'], ['git', 'add', '.'],
                         ['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@invalid', 'commit', '-qm', 'frozen input']):
                p = pair.call(argv, checkout)
                assert p.returncode == 0, p.stderr
            pair.runner.preflight(old['binary'], {'provider': 'codex', 'profile': 'edit', 'cwd': str(checkout)}, pair.runner.worker_env('codex'))
        for name in ('SKILL.md', 'references/delegation.md', 'references/waiting.md'):
            p = arm / 'policy' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(luna.POLICY / name, p)
        shutil.copy2(previous / 'contract-schema.json', arm / 'contract-schema.json')
        shutil.copy2(Path(read(HERE / 'local-luna.json')['root']) / 'handoff-schema.json', arm / 'handoff-schema.json')
        worker_name = 'Luna Max through Codex CLI' if kind == 'luna' else 'MiMo-V2.6-Pro thinking through Kilo CLI'
        plan = (common + f'This stage is preparation only. Read {arm / "policy/SKILL.md"} and its '
                'references/delegation.md, plus TASK.md and only necessary starting evidence. '
                f'Produce one implementation assignment for {worker_name}, as JSON matching the supplied schema. '
                'Do not edit files or solve the adapters first. The host runs one worker and resumes this same '
                'Sol session for acceptance. Do not launch or poll workers. Assign the whole batch, development '
                'checks and corrections together. Use read_paths ["TASK.md","imports","check_contract.py",'
                '"fixtures.json","boundaries_visible.py","protected_hashes.json","test_adapters.py"]. '
                'Write_paths must name the six adapters and optional imports/adapters/_shared.py and test_adapters.py '
                'only. This single worker and provider use on this synthetic task are authorized. '
                'No other workers or external services. The worker has no iteration cap and a 30-minute timeout.')
        (arm / 'plan-prompt.txt').write_text(plan, encoding='utf-8')
        (arm / 'solo-prompt.txt').write_text(common + 'Do all implementation and verification yourself. Return the supplied result schema.', encoding='utf-8')
        acceptance = (Path(read(HERE / 'local-luna.json')['root']) / 'accept-prompt.txt').read_text().replace('Luna', 'worker')
        if kind == 'mimo':
            acceptance = acceptance.replace('WORKER-RESULT.json', 'KILO-RESULT.json')
        (arm / 'accept-prompt.txt').write_text(acceptance, encoding='utf-8')
        m = {k: old[k] for k in ('binary', 'config', 'model', 'effort', 'owned', 'sol_timeout_seconds')}
        m.update(root=str(arm), worker_model='gpt-5.6-luna', worker_effort='max',
                 worker_timeout_seconds=1800, public_cases=150, held_out_cases=104, arm=kind)
        frozen = shared_scripts + [p for p in arm.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
        m['frozen'] = {str(p.resolve()): pair.sha(p) for p in frozen}
        save(arm / 'manifest.json', m)
        save(root / (kind + '-pointer.json'), {'root': str(arm)})
    settings = read(pair.KILO / 'settings.json')
    assert settings['steps'] is None
    config = pair.kd.make_config({'mode': 'implement'}, settings['model'], settings['variant'], None)
    pair.kd.resolved_profile(pair.kd.kilo_executable(), root / 'mimo/delegated/task',
                            pair.kd.child_env(root, config), root, config)
    versions = {name: pair.call([binary, '--version'], root).stdout.strip() for name, binary in
                [('codex', old['binary']), ('kilo', pair.kd.kilo_executable())]}
    plan = {'order': order, 'shuffle_seed': 20260922, 'binary': old['binary'], 'thread': os.environ['CODEX_THREAD_ID'],
            'rates_per_million': accounting.RATES, 'versions': versions, 'cases': [150, 104],
            'source_hashes': {p.relative_to(source).as_posix(): pair.sha(p) for p in source.rglob('*') if p.is_file()},
            'prepared_at': time.time(), 'automatic_retry': False}
    save(root / 'run-plan.json', plan)
    save(POINTER, {'root': str(root)})
    save(root / 'notify-request.json', {'codex': old['binary'], 'thread': plan['thread'], 'cwd': str(pair.REPO),
         'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run'], 'receipt': str(root / 'result.json')})
    print(json.dumps({'prepared': str(root), 'order': order, 'cases': plan['cases'], 'paid_calls': 0}))


def run():
    root = Path(read(POINTER)['root'])
    plan = read(root / 'run-plan.json')
    with (root / 'started.json').open('x') as f:
        json.dump({'started_at': time.time()}, f)
    result = {'started_at': time.time(), 'arms': {}, 'automatic_retry': False}
    try:
        for kind in plan['order']:
            result['active_arm'] = kind
            save(root / 'result.json', result)
            arm = root / kind
            print(kind + ' started', flush=True)
            if kind == 'solo':
                m = read(arm / 'manifest.json')
                assert all(pair.sha(p) == h for p, h in m['frozen'].items()), 'Frozen input changed'
                tid = pair.sol(arm, m, 'delegated', 'solo', (arm / 'solo-prompt.txt').read_text(), schema=arm / 'handoff-schema.json')
                state = {'status': 'finished', 'sessions': {'sol': tid},
                         'grade_exit_code': pair.grade(arm, arm / 'delegated/task', 'solo-grade')}
                save(arm / 'result.json', state)
            else:
                module = luna if kind == 'luna' else uncapped
                module.POINTER = root / (kind + '-pointer.json')
                exit_code = module.run()
                state = read(arm / 'result.json')
                assert exit_code == 0, state
            result['arms'][kind] = state
            save(root / 'result.json', result)
        result['status'] = 'finished'
    except Exception as exc:
        result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        result['finished_at'] = time.time()
        save(root / 'result.json', result)
        print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'finished' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run'])
    args = parser.parse_args()
    raise SystemExit(globals()[args.action]())
