"""Run exactly six sequential trials. A=solo; B in this report uses runner C.

Invoke only after user authorization for the six model runs. No automatic retries.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = HERE.parent / 'pilot/run.py'


def hashes(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}


def main():
    fixture = json.loads((HERE / 'local-fixture.json').read_text())
    root = Path(fixture['root'])
    plan_path = root / 'run-plan.json'
    if plan_path.exists():
        raise SystemExit('Run plan already exists. No automatic reruns or duplicate billing.')
    suites = [('repair', 'A'), ('repair', 'C'), ('investigation', 'C'),
              ('investigation', 'A'), ('component', 'A'), ('component', 'C')]
    locked = [RUNNER, Path(__file__)]
    for name in ('repair', 'investigation', 'component'):
        locked.extend(p for p in (HERE / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        if not (HERE / name / 'grade.py').is_file():
            raise SystemExit('Missing completed fixture: ' + name)
    locked.extend(p for p in Path(fixture['skill_source']).rglob('*') if p.is_file())
    locked.extend(p for p in Path(fixture['investigation_source']).rglob('*') if p.is_file())
    locked.append(Path(fixture['investigation_truth']))
    frozen = hashes(locked)
    plan = {'timeout_seconds': 2700, 'report_mapping': {'A': 'A', 'C': 'B: revised skill'},
            'order': suites, 'frozen_sha256': frozen, 'runs': []}
    plan_path.write_text(json.dumps(plan, indent=2), encoding='utf-8')
    for number, (name, arm) in enumerate(suites, 1):
        if hashes(locked) != frozen:
            raise SystemExit('Frozen fixture/skill/runner changed; stopping before another paid run.')
        command = [sys.executable, '-B', '-X', 'utf8', str(RUNNER), arm,
                   '--suite', str(HERE / name), '--skill-source', fixture['skill_source'],
                   '--python', fixture['python'], '--timeout-seconds', '2700']
        if name == 'investigation':
            command += ['--source', fixture['investigation_source']]
        if arm == 'C':
            command += ['--allow-claude']
        log_path = root / f'{number:02}-{name}-{arm}.log'
        print(json.dumps({'starting': number, 'task': name, 'arm': arm, 'log': str(log_path)}), flush=True)
        started = time.time()
        with log_path.open('w', encoding='utf-8') as log:
            proc = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
        run_path = None
        for line in log_path.read_text(encoding='utf-8').splitlines():
            try:
                message = json.loads(line)
            except ValueError:
                continue
            if 'prepared' in message:
                run_path = Path(message['prepared'])
        result = json.loads((run_path / 'result.json').read_text()) if run_path and (run_path / 'result.json').exists() else None
        plan['runs'].append({'task': name, 'arm': arm, 'started_unix': started,
                             'runner_exit': proc.returncode, 'run_directory': str(run_path) if run_path else None,
                             'result': result})
        plan_path.write_text(json.dumps(plan, indent=2), encoding='utf-8')
        print(json.dumps({'finished': number, 'task': name, 'result': result, 'runner_exit': proc.returncode}), flush=True)
        if proc.returncode or result is None:
            raise SystemExit('Harness failure: preserved evidence; stopping before further model calls.')
    if hashes(locked) != frozen:
        raise SystemExit('Frozen input changed during final run: comparison requires audit.')
    print(json.dumps({'complete': True, 'plan': str(plan_path)}), flush=True)


if __name__ == '__main__':
    main()
