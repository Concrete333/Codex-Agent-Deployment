"""One explicit-delegation control, reusing the frozen runner and corpus.

prepare/summarize make no model calls. run launches exactly one trial, once.
The generated runner differs by one prompt-append line; the original is untouched.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from experiment import module, save

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DIRECTIVE = ('Required execution: use the supplied skill. Delegate the complete TASK.md deliverable '
             'to one gpt-5.6-luna worker at max effort with fork_turns="none". Keep the assignment brief; '
             'the worker owns reading, answer writing and local checks. Retain final verification. '
             'Do not launch other workers.')


def frozen_ok(plan):
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h
               for p, h in plan['frozen_sha256'].items()), 'Frozen inputs changed'


def parse_run(log):
    for line in log.splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if 'prepared' in row:
            return Path(row['prepared'])
    raise RuntimeError('No prepared run receipt; inspect retained log')


def main(mode):
    fixture = json.loads((HERE / 'local-fixture.json').read_text())
    original_root = Path(fixture['root'])
    original_plan = json.loads((original_root / 'run-plan.json').read_text())
    frozen_ok(original_plan)
    root = original_root / 'forced-luna'
    runner = root / 'runner-forced-luna.py'
    command = [sys.executable, '-B', '-X', 'utf8', str(runner), 'C', '--suite', str(HERE),
               '--source', fixture['source'], '--python', fixture['python'],
               '--skill-source', fixture['skill_source'], '--timeout-seconds', '2700', '--allow-claude']
    if mode == 'prepare':
        root.mkdir(exist_ok=False)
        original = (HERE.parent / 'pilot/run.py').read_text(encoding='utf-8')
        anchor = "    (run / 'prompt.txt').write_text(prompt, encoding='utf-8')"
        assert original.count(anchor) == 1
        added_line = '    prompt += ' + repr('\n' + DIRECTIVE + '\n') + '\n'
        runner.write_text(original.replace(anchor, added_line + anchor), encoding='utf-8')
        assert runner.read_text(encoding='utf-8').replace(added_line, '', 1) == original
        preflight = subprocess.run(command + ['--prepare-only'], cwd=REPO, capture_output=True,
                                   text=True, encoding='utf-8', timeout=120)
        (root / 'preflight.log').write_text(preflight.stdout + preflight.stderr, encoding='utf-8')
        if preflight.returncode:
            raise RuntimeError('Preflight failed; no model call made')
        prepared = parse_run(preflight.stdout)
        prior = Path(next(r['run_directory'] for r in original_plan['runs'] if r['arm'] == 'C'))
        before = json.loads((prior / 'manifest.json').read_text())
        after = json.loads((prepared / 'manifest.json').read_text())
        for key in ('task_tree', 'configs', 'skill_sha256', 'policy_sha256', 'grader_sha256'):
            assert before[key] == after[key], key
        assert (prepared / 'prompt.txt').read_text(encoding='utf-8') == (
            (prior / 'prompt.txt').read_text(encoding='utf-8') + '\n' + DIRECTIVE + '\n')
        inspected = (prepared / 'prompt-inspection.json').read_text(encoding='utf-8')
        assert not any(x in inspected for x in ('cases.json', 'source-audit.json', 'expected_disposition', '### Available skills'))
        frozen = dict(original_plan['frozen_sha256'])
        for p in (runner, Path(__file__)):
            frozen[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        save(root / 'run-plan.json', {'condition': 'D: skill + required Luna Max', 'directive': DIRECTIVE,
                                    'frozen_sha256': frozen, 'preflight': str(prepared), 'runs': []})
        save(root / 'local-fixture.json', dict(fixture, root=str(root)))
        print(json.dumps({'preflight_passed': True, 'directive_words': len(DIRECTIVE.split()),
                          'identical_base_prompt': True, 'root': str(root)}))
        return
    plan = json.loads((root / 'run-plan.json').read_text())
    frozen_ok(plan)
    if mode == 'summarize':
        summary = module('existing_accounting', HERE.parent / 'revision-ab/summarize.py')
        summary.HERE = root
        summary.main()
        return
    with (root / 'started.json').open('x', encoding='utf-8') as marker:
        json.dump({'command': command}, marker)
    print('Starting D: required Luna Max, unchanged skill and task.', flush=True)
    log = root / 'run.log'
    with log.open('w', encoding='utf-8') as stream:
        proc = subprocess.run(command, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT)
    run = parse_run(log.read_text(encoding='utf-8'))
    result_path = run / 'result.json'
    result = json.loads(result_path.read_text()) if result_path.exists() else None
    plan['runs'].append({'task': 'prose-migration-forced-luna', 'arm': 'D', 'runner_arm': 'C',
                        'run_directory': str(run), 'runner_exit': proc.returncode, 'result': result})
    save(root / 'run-plan.json', plan)
    frozen_ok(plan)
    print(json.dumps(plan['runs'][0]), flush=True)
    if proc.returncode or result is None:
        raise SystemExit('Harness failed; original artifacts retained; no automatic retry')


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('prepare', 'run', 'summarize'):
        raise SystemExit('Usage: forced_luna.py prepare|run|summarize')
    main(sys.argv[1])
