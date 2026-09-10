"""External grading: frozen Self checks and frozen baseline regressions."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REGRESSIONS = ('test_baseconverter.py', 'test_converter.py', 'test_cols.py', 'test_copy.py',
               'test_dataclasses.py', 'test_factory_hooks.py', 'test_gen.py', 'test_gen_dict.py',
               'test_generics.py', 'test_optionals.py', 'test_recursive.py', 'test_typeddicts.py')


def main():
    target = Path(sys.argv[1]).resolve()
    fixture = json.loads((HERE / 'local-fixture.json').read_text(encoding='utf-8'))
    env = dict(os.environ, PYTHONPATH=str(target / 'src'), FAST='1', PYTHONDONTWRITEBYTECODE='1')
    acceptance = subprocess.run([sys.executable, '-B', str(HERE / 'test_acceptance.py')],
                                cwd=target, env=env, timeout=30)
    baseline = Path(fixture['baseline'])
    regression = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-o', 'addopts=',
                                '-p', 'no:cacheprovider', '-q', '--hypothesis-seed=1701',
                                *[str(baseline / 'tests' / name) for name in REGRESSIONS]],
                               cwd=target, env=env, timeout=120)
    print(json.dumps({'acceptance_exit_code': acceptance.returncode,
                      'regression_exit_code': regression.returncode}), flush=True)
    raise SystemExit(bool(acceptance.returncode or regression.returncode))


if __name__ == '__main__':
    main()
