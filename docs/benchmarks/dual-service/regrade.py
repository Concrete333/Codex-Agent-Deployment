"""Offline regrading of saved task directories; never invokes a model.

Usage: python regrade.py A=PATH B=PATH C1=PATH C2=PATH
Detailed logs and file hashes go to one temporary directory.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for package in ('feed', 'retryq') for p in sorted((root / package).rglob('*.py'))
            if '__pycache__' not in p.parts}


def main():
    run = Path(tempfile.mkdtemp(prefix='agent-deployment-regrade-v2-'))
    records = []
    for index, item in enumerate(sys.argv[1:]):
        label, target = item.split('=', 1)
        path = Path(target).resolve()
        if not path.is_dir():
            raise ValueError(f'Missing task: {path}')
        before = hashes(path)
        grades = {}
        for filename in ('grade.py', 'grade_v2.py'):
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(HERE / filename), str(path), '-q'],
                                    capture_output=True, text=True, encoding='utf-8', timeout=30)
            log = run / f'{index}-{filename}.log'
            log.write_text(result.stdout + result.stderr, encoding='utf-8')
            grades[filename] = dict(exit_code=result.returncode, log=str(log))
        unchanged = before == hashes(path)
        record = dict(label=label, task=str(path), grades=grades,
                      production_sources_unchanged=unchanged, source_hashes=before)
        records.append(record)
        print(json.dumps({k: v for k, v in record.items() if k != 'source_hashes'}))
        if not unchanged:
            raise RuntimeError('Saved source changed during grading')
    (run / 'results.json').write_text(json.dumps(dict(
        grader_hashes={name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                       for name in ('grade.py', 'grade_v2.py')}, trials=records), indent=2), encoding='utf-8')
    print(json.dumps({'receipts': str(run)}))


if __name__ == '__main__':
    main()
