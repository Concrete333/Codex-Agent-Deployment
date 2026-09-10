"""Regrade saved investigation artifacts without model calls or source edits.

The oracle/source paths in local-fixture.json may point to byte-identical readable
copies. Original trial logs and frozen graders are never replaced.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BINARY = Path.home() / 'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'


def file_hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()
            and not any(part in ('.git', '.benchmark-policy', '__pycache__') for part in p.relative_to(root).parts)}


def inside(target):
    before = file_hashes(target)
    grade = subprocess.run([sys.executable, '-B', str(HERE / 'investigation/grade.py'), str(target)],
                           cwd=target, capture_output=True, text=True, encoding='utf-8', timeout=120)
    after = file_hashes(target)
    print(json.dumps({'grade_exit_code': grade.returncode, 'stdout': grade.stdout, 'stderr': grade.stderr,
                      'artifact_sha256_before': before, 'artifact_sha256_after': after,
                      'artifacts_unchanged': before == after}))


def main():
    fixture = json.loads((HERE / 'local-fixture.json').read_text())
    root = Path(fixture['root'])
    plan = json.loads((root / 'run-plan.json').read_text())
    if len(plan['runs']) != 6:
        raise SystemExit('Finish the six frozen trials before offline regrading.')
    original_source = root / 'investigation-source'
    original_truth = root / 'investigation-truth.json'
    assert file_hashes(original_source) == file_hashes(Path(fixture['investigation_source']))
    assert original_truth.read_bytes() == Path(fixture['investigation_truth']).read_bytes()
    for run in plan['runs']:
        if run['task'] != 'investigation':
            continue
        target = Path(run['run_directory']) / 'task'
        grade = subprocess.run([str(BINARY), 'sandbox', '-P', ':read-only', '-C', str(target),
                                '-c', 'windows.sandbox="elevated"', '--', sys.executable,
                                '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--inside', str(target)],
                               capture_output=True, text=True, encoding='utf-8', timeout=180)
        if grade.returncode:
            raise RuntimeError(grade.stdout + grade.stderr)
        receipt = json.loads(grade.stdout)
        receipt.update(oracle_source_copies_identical=True, original_oracle=str(original_truth),
                       readable_oracle=fixture['investigation_truth'],
                       grader_sha256=hashlib.sha256((HERE / 'investigation/grade.py').read_bytes()).hexdigest())
        (Path(run['run_directory']) / 'offline-regrade.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        print(json.dumps({'arm': run['arm'], 'grade_exit_code': receipt['grade_exit_code'],
                          'artifacts_unchanged': receipt['artifacts_unchanged'], 'stderr': receipt['stderr']}))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--inside':
        inside(Path(sys.argv[2]).resolve())
    else:
        main()
