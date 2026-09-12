"""Frozen external conformance, held-out cases and scope checks. No model calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    fixture = json.loads((HERE / 'local-fixture.json').read_text(encoding='utf-8'))
    source, target = Path(fixture['source']), Path(sys.argv[1]).resolve()
    expected = json.loads((source / 'protected_hashes.json').read_text(encoding='utf-8'))
    expected['protected_hashes.json'] = hashlib.sha256((source/'protected_hashes.json').read_bytes()).hexdigest()
    changed = [name for name, digest in expected.items() if not (target/name).is_file()
               or hashlib.sha256((target/name).read_bytes()).hexdigest() != digest]
    allowed = set(expected) | {'imports/adapters/' + fmt + '.py' for fmt in fixture['formats']} | {'imports/adapters/_shared.py'}
    unexpected = [p.relative_to(target).as_posix() for p in target.rglob('*.py')
                  if '.benchmark-policy' not in p.parts and '__pycache__' not in p.parts
                  and p.relative_to(target).as_posix() not in allowed and not p.name.startswith('test_')]
    if changed or unexpected:
        print(json.dumps({'passed': False, 'changed_protected_files': changed, 'unexpected_python_files': unexpected}))
        return 1
    results = []
    for label, case_path in [('public', source/'fixtures.json'), ('held_out', Path(fixture['root'])/'held-out.json')]:
        proc = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(source/'check_contract.py'), str(target), str(case_path)],
                              cwd=target, capture_output=True, text=True, encoding='utf-8', timeout=60)
        results.append({'check': label, 'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
    tests = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-q'], cwd=target,
                           capture_output=True, text=True, encoding='utf-8', timeout=60)
    # Added tests are optional. Python 3.13 returns 5 when discovery finds none;
    # retain that status without failing an otherwise valid reference/submission.
    no_tests = tests.returncode == 5 and 'Ran 0 tests' in tests.stderr and 'NO TESTS RAN' in tests.stderr
    results.append({'check': 'added_tests', 'exit_code': tests.returncode, 'not_applicable': no_tests,
                    'stdout': tests.stdout, 'stderr': tests.stderr})
    passed = all(r['exit_code']==0 or r.get('not_applicable',False) for r in results)
    print(json.dumps({'passed': passed, 'checks': results}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
