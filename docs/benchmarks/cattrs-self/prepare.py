"""Prepare a pinned upstream fixture and private Python 3.12 environment. No models."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
BASE = 'ec5383376ced63c1dfb8d98b9307f7226c98d53a'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', required=True, type=Path, help='Python 3.12 executable')
    args = parser.parse_args()
    version = subprocess.check_output([str(args.python), '-c', 'import sys; print(sys.version_info[:2])'], text=True)
    if version.strip() != '(3, 12)':
        parser.error('This frozen fixture uses Python 3.12')
    root = Path(tempfile.mkdtemp(prefix='agent-deployment-cattrs-prep-'))
    source, venv = root / 'source', root / 'venv312'
    subprocess.run(['git', 'clone', '--quiet', '--depth', '1', '--branch', 'v24.1.3',
                    'https://github.com/python-attrs/cattrs.git', str(source)], check=True)
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != BASE:
        raise RuntimeError('Upstream tag no longer matches the frozen commit')
    shutil.copy2(HERE / 'TASK.md', source / 'TASK.md')
    subprocess.run([str(args.python), '-m', 'venv', str(venv)], check=True)
    runtime = venv / 'Scripts/python.exe'
    subprocess.run([str(runtime), '-m', 'pip', 'install', '--quiet', '-r', str(HERE / 'requirements-lock.txt')], check=True)
    fixture = dict(baseline=str(source), python=str(runtime))
    (HERE / 'local-fixture.json').write_text(json.dumps(fixture, indent=2), encoding='utf-8')
    print(json.dumps(fixture), flush=True)


if __name__ == '__main__':
    main()
