"""Small local A/B/C smoke test. No dependencies, API keys or global config edits.

Usage: python run.py A|B|C [--prepare-only]
Each invocation creates a fresh temporary task copy and retains local receipts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SKILL = REPO
BINARY = Path.home() / 'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arm', choices=['A', 'B', 'C'])
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    run = Path(tempfile.mkdtemp(prefix=f'agent-deployment-pilot-{args.arm}-'))
    task = run / 'task'
    shutil.copytree(HERE / 'task', task, ignore=shutil.ignore_patterns('__pycache__'))
    subprocess.run(['git', 'init', '-q', str(task)], check=True)
    subprocess.run(['git', '-C', str(task), 'add', '.'], check=True)
    base = subprocess.run(['git', '-C', str(task), 'write-tree'], check=True,
                          capture_output=True, text=True).stdout.strip()
    configs = {
        'model_reasoning_effort': 'high', 'approval_policy': 'never',
        'windows.sandbox': 'elevated', 'project_doc_max_bytes': 0,
        'features.memories': False, 'features.plugins': False,
        'features.remote_plugin': False,
        'memories.use_memories': False, 'memories.generate_memories': False,
        'agents.enabled': args.arm != 'A',
        'agents.max_concurrent_threads_per_session': 2,
        'features.multi_agent': args.arm != 'A',
        'features.multi_agent_v2.enabled': args.arm != 'A',
        'features.multi_agent_v2.min_wait_timeout_ms': 1500000,
        'features.multi_agent_v2.default_wait_timeout_ms': 1500000,
        'features.multi_agent_v2.max_wait_timeout_ms': 1500000,
        'web_search': 'disabled',
    }
    overrides = []
    for key, value in configs.items():
        overrides += ['-c', f'{key}={json.dumps(value)}']
    # Host discovery suppression does not disable locally discovered skills.
    skills = sorted({str(p.resolve()).replace('\\', '/')
                     for root in (Path.home() / '.codex/skills', Path.home() / '.agents/skills')
                     for p in root.rglob('SKILL.md')})
    disabled = ','.join('{path=' + json.dumps(p) + ',enabled=false}' for p in skills)
    overrides += ['-c', 'skills.config=[' + disabled + ']']
    prompt = (task / 'TASK.md').read_text(encoding='utf-8')
    prompt += '\nCoordinator: gpt-6-astra at high; keep this configuration. '
    prompt += 'Use only this task checkout, except reading the deployment policy when explicitly requested below. '
    prompt += 'Do not inspect personal skills, memory, logs, other repositories or other trials. '
    if args.arm == 'A':
        prompt += 'Complete this task yourself; delegation is disabled.\n'
    else:
        prompt += ('Native GPT subagents are authorized if useful, with at most two active children. '
                   'Available worker models: gpt-5.6-luna, gpt-5.6-terra, gpt-5.6-sol, gpt-6-astra; '
                   'efforts: low, medium, high, xhigh, max. No Claude or external agent processes in this pilot.\n')
    if args.arm == 'C':
        policy = task / '.benchmark-policy'
        policy.mkdir()
        shutil.copy2(SKILL / 'SKILL.md', policy / 'SKILL.md')
        shutil.copytree(SKILL / 'references', policy / 'references')
        prompt += ('Use the agent-deployment skill at .benchmark-policy/SKILL.md for this task. '
                   'Read its references as directed. Do not modify .benchmark-policy. '
                   'If the skill cannot be read, stop and report blocked; do not perform a substitute no-skill run.\n')
    (run / 'prompt.txt').write_text(prompt, encoding='utf-8')
    command = [str(BINARY), 'exec', '--ignore-user-config', '--ignore-rules', '--strict-config',
               '--json', '--color', 'never', '-s', 'workspace-write', '-m', 'gpt-6-astra',
               '-C', str(task), *overrides, '-']
    manifest = {'arm': args.arm, 'task_tree': base, 'command': command, 'disabled_skills': skills,
                'configs': configs, 'timeout_seconds': 900,
                'skill_sha256': hashlib.sha256((SKILL / 'SKILL.md').read_bytes()).hexdigest(),
                'run_directory': str(run), 'parent_model': 'gpt-6-astra', 'parent_effort': 'high'}
    (run / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'prepared': str(run), 'arm': args.arm, 'task_tree': base}), flush=True)
    if args.prepare_only:
        # Read-only prompt inspection; never starts an inference request.
        debug = subprocess.run([str(BINARY), *overrides, 'debug', 'prompt-input', prompt],
                               cwd=task, capture_output=True, text=True, encoding='utf-8', timeout=30)
        (run / 'prompt-inspection.json').write_text(debug.stdout, encoding='utf-8')
        if debug.returncode or '### Available skills' in debug.stdout:
            raise RuntimeError('Skill isolation preflight failed; inspect the saved prompt dump')
        print('No discovered skill catalogue in preflight; global instructions are held constant.')
        return
    env = dict(os.environ)
    env.pop('OPENAI_API_KEY', None)
    env.pop('CODEX_API_KEY', None)
    env['PYTHONUTF8'] = '1'
    started = time.monotonic()
    timed_out = False
    with (run / 'events.jsonl').open('w', encoding='utf-8') as events, (run / 'stderr.log').open('w', encoding='utf-8') as errors:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=events, stderr=errors,
                                text=True, encoding='utf-8', env=env, cwd=task)
        try:
            proc.communicate(prompt, timeout=900)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                           capture_output=True, timeout=20, check=True)
            proc.wait(timeout=20)
    grade = None
    if not timed_out and proc.returncode == 0:
        with (run / 'grade.log').open('w', encoding='utf-8') as log:
            graded = subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'grade.py'), str(task)],
                                    cwd=task, stdout=log, stderr=subprocess.STDOUT, timeout=30)
            grade = graded.returncode
    with (run / 'diff.patch').open('w', encoding='utf-8') as diff:
        subprocess.run(['git', '-C', str(task), 'diff'], stdout=diff, check=True)
    result = {'arm': args.arm, 'exit_code': proc.returncode, 'timed_out': timed_out,
              'seconds': round(time.monotonic() - started, 2), 'grade_exit_code': grade,
              'run_directory': str(run)}
    for line in (run / 'events.jsonl').read_text(encoding='utf-8').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'thread.started':
            result['thread_id'] = event.get('thread_id')
        if event.get('type') == 'turn.completed':
            result['reported_turn_usage'] = event.get('usage')
    (run / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
