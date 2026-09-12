"""Independent read-only evaluation; no inference or participant-file writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    fixture = json.loads((HERE / 'local-fixture.json').read_text(encoding='utf-8'))
    source, target = Path(fixture['source']), Path(sys.argv[1]).resolve()
    protected = json.loads((source / 'protected_hashes.json').read_text(encoding='utf-8'))
    protected['protected_hashes.json'] = hashlib.sha256((source / 'protected_hashes.json').read_bytes()).hexdigest()
    changed = [name for name, digest in protected.items()
               if not (target / name).is_file() or hashlib.sha256((target / name).read_bytes()).hexdigest() != digest]
    if changed:
        print(json.dumps({'passed': False, 'protected_files_changed': changed}))
        return 1
    results = []
    for command in ([sys.executable, '-B', str(source / 'check_contract.py'), str(target)],
                    [sys.executable, '-B', '-m', 'unittest', 'discover', '-q']):
        done = subprocess.run(command, cwd=target, capture_output=True, text=True, encoding='utf-8', timeout=60)
        results.append({'command': command[2:], 'exit_code': done.returncode,
                        'stdout': done.stdout, 'stderr': done.stderr})
    print(json.dumps({'passed': all(r['exit_code'] == 0 for r in results), 'checks': results}, indent=2))
    return 0 if all(r['exit_code'] == 0 for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
