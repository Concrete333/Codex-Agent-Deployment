"""Offline preflight/accounting and one guarded sequential A/C pair."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def load():
    return json.loads((HERE / 'local-fixture.json').read_text(encoding='utf-8'))


def frozen(fixture):
    paths = list(HERE.glob('*.py')) + [Path(fixture['runner'])]
    for field in ('source', 'policy'):
        paths += [p for p in Path(fixture[field]).rglob('*') if p.is_file()]
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def command(fixture, arm, prepare=False):
    cmd = [fixture['python'], '-B', '-X', 'utf8', fixture['runner'], arm,
           '--suite', str(HERE), '--source', fixture['source'], '--python', fixture['python'],
           '--skill-source', fixture['policy'], '--timeout-seconds', '1200']
    return cmd + ['--prepare-only'] if prepare else cmd


def preflight(fixture):
    root = Path(fixture['root'])
    destination = root / 'preflight'
    destination.mkdir(exist_ok=False)
    results = []
    reference = Path(fixture['reference'])
    original = (reference / 'dispatchboard/idempotency.py').read_text(encoding='utf-8')
    variants = {'reference': original,
                'receipt_alias': original.replace('return copy.deepcopy(current[2])', 'return current[2]'),
                'exclusive_expiry': original.replace('now >= current[0]', 'now > current[0]'),
                'overflow_rejection': (HERE.parent / 'revision-ab/component/reference.py').read_text(encoding='utf-8'),
                'checker_tamper': original}
    for name, code in variants.items():
        target = destination / name
        shutil.copytree(reference, target)
        (target / 'dispatchboard/idempotency.py').write_text(code, encoding='utf-8')
        if name == 'checker_tamper':
            with (target / 'check_contract.py').open('a', encoding='utf-8') as stream:
                stream.write('\n# changed checker\n')
        done = subprocess.run([fixture['python'], '-B', str(HERE / 'grade.py'), str(target)],
                              capture_output=True, text=True, encoding='utf-8', timeout=90)
        save(destination / (name + '.json'), {'exit_code': done.returncode, 'stdout': done.stdout, 'stderr': done.stderr})
        expected = done.returncode == 0 if name == 'reference' else done.returncode != 0
        results.append({'case': name, 'exit_code': done.returncode, 'expected': expected})
        assert expected, name
    binary = Path.home() / 'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
    sandbox = subprocess.run([str(binary), 'sandbox', '-P', ':read-only', '-C', str(reference),
                              '-c', 'windows.sandbox="elevated"', '--', fixture['python'], '-B', '-X', 'utf8',
                              str(HERE / 'grade.py'), str(reference)],
                             capture_output=True, text=True, encoding='utf-8', timeout=90)
    save(destination / 'sandbox.json', {'exit_code': sandbox.returncode, 'stdout': sandbox.stdout, 'stderr': sandbox.stderr})
    assert sandbox.returncode == 0, 'Reference must pass through actual sandbox grading route'
    for arm in ('A', 'C'):
        done = subprocess.run(command(fixture, arm, True), cwd=REPO, capture_output=True,
                              text=True, encoding='utf-8', timeout=90)
        save(destination / (arm + '-prompt.json'), {'exit_code': done.returncode, 'stdout': done.stdout, 'stderr': done.stderr})
        assert done.returncode == 0, 'Prompt preflight ' + arm
    save(root / 'preflight.json', {'passed': True, 'mutants': results, 'frozen': frozen(fixture)})
    print(json.dumps({'passed': True, 'checks': results, 'sandbox': sandbox.returncode}))


def run(fixture):
    root = Path(fixture['root'])
    preflight_result = json.loads((root / 'preflight.json').read_text(encoding='utf-8'))
    assert preflight_result['passed'] and preflight_result['frozen'] == frozen(fixture)
    marker = root / 'started.json'
    with marker.open('x', encoding='utf-8') as stream:
        json.dump({'order': ['A', 'C'], 'timeout_seconds': 1200, 'automatic_retry': False}, stream)
    plan = {'order': ['A', 'C'], 'frozen': frozen(fixture), 'runs': []}
    save(root / 'run-plan.json', plan)
    for arm in plan['order']:
        assert plan['frozen'] == frozen(fixture), 'Frozen inputs changed'
        print(json.dumps({'starting': arm}), flush=True)
        with (root / (arm + '.log')).open('w', encoding='utf-8') as stream:
            done = subprocess.run(command(fixture, arm), cwd=REPO, stdout=stream, stderr=subprocess.STDOUT)
        run_dir = None
        for line in (root / (arm + '.log')).read_text(encoding='utf-8').splitlines():
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if 'prepared' in item:
                run_dir = Path(item['prepared'])
        result_file = run_dir / 'result.json' if run_dir else None
        result = json.loads(result_file.read_text(encoding='utf-8')) if result_file and result_file.exists() else None
        row = {'arm': arm, 'runner_exit': done.returncode, 'run_directory': str(run_dir), 'result': result}
        plan['runs'].append(row)
        save(root / 'run-plan.json', plan)
        print(json.dumps(row), flush=True)
        if done.returncode != 0 or result is None:
            raise SystemExit('Harness failed; no automatic continuation or retry.')
    assert plan['frozen'] == frozen(fixture)


def summarize(fixture):
    spec = importlib.util.spec_from_file_location('usage_accounting', HERE.parent / 'revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    root = Path(fixture['root'])
    plan = json.loads((root / 'run-plan.json').read_text(encoding='utf-8'))
    index = accounting.session_index()
    rows = []
    for run in plan['runs']:
        tid = run['result']['thread_id']
        descendants = {tid}
        while True:
            found = {key for key, item in index.items() if item['parent'] in descendants}
            if found <= descendants:
                break
            descendants.update(found)
        agents = [accounting.audit_thread(key, index[key]) for key in sorted(descendants)]
        assert all(a.get('reconciled') for a in agents), 'Unreconciled usage'
        row = {**run, 'agents': agents, 'api_equivalent_usd': round(sum(a['api_equivalent_usd'] for a in agents), 9)}
        rows.append(row)
        print(json.dumps({'arm': row['arm'], 'api_equivalent_usd': row['api_equivalent_usd'],
                          'agents': len(agents), 'result': row['result']}))
    save(root / 'accounting.json', {'rates_per_million': accounting.RATES, 'runs': rows,
                                  'note': 'Captured trial costs only; preparation, supervision and external evaluation excluded.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('preflight', 'run', 'summarize'))
    args = parser.parse_args()
    globals()[args.operation](load())
