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
    parser.add_argument('--source', type=Path, help='Prepared external task checkout; default suite/task')
    parser.add_argument('--python', type=Path, help='Prepared Python environment for workers and grading')
    parser.add_argument('--skill-source', type=Path, default=SKILL, help='Frozen operational skill snapshot')
    parser.add_argument('--timeout-seconds', type=int, default=900, help='Equal per-run safety limit')
    parser.add_argument('--allow-claude', action='store_true', help='Authorize Opus 5 via supplied wrapper in C')
    parser.add_argument('--suite', type=Path, default=HERE, help='Directory containing task/ and grade.py')
    parser.add_argument('--grader', choices=['grade.py', 'grade_v2.py'], default='grade.py',
                        help='Explicit evaluation version; historical runs use grade.py')
    args = parser.parse_args()
    if args.timeout_seconds <= 0 or (args.allow_claude and args.arm != 'C'):
        parser.error('Positive timeout required; Claude option is supported only for skill condition C')
    skill_source = args.skill_source.resolve()
    suite = args.suite.resolve()
    source = args.source.resolve() if args.source else suite / 'task'
    runtime = args.python.resolve() if args.python else Path(sys.executable)
    grader = suite / args.grader
    if not (source / 'TASK.md').is_file() or not grader.is_file() or not runtime.is_file():
        parser.error('Source must contain TASK.md; grader and Python executable must exist')
    contract = suite / 'contract-v2.md' if args.grader == 'grade_v2.py' else None
    if contract is not None and not contract.is_file():
        parser.error('Version 2 requires contract-v2.md')
    run = Path(tempfile.mkdtemp(prefix=f'agent-deployment-{suite.name}-{args.arm}-'))
    task = run / 'task'
    shutil.copytree(source, task, ignore=shutil.ignore_patterns('__pycache__', '.git', '.pytest_cache', '.hypothesis'))
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
    if contract is not None:
        shutil.copy2(contract, task / 'CONTRACT-V2.md')
        prompt += '\n' + contract.read_text(encoding='utf-8')
    prompt += '\nCoordinator: gpt-6-astra at high; keep this configuration. '
    if args.python:
        prompt += f'Prepared Python executable: {runtime}. Use it for all Python/test commands. '
    prompt += 'Use only this task checkout, except reading the deployment policy when explicitly requested below. '
    prompt += 'Do not inspect personal skills, memory, logs, other repositories or other trials. '
    if args.arm == 'A':
        prompt += 'Complete this task yourself; delegation is disabled.\n'
    else:
        prompt += ('Native GPT subagents are authorized if useful, with at most two active children. '
                   'Available worker models: gpt-5.6-luna, gpt-5.6-terra, gpt-5.6-sol'
                   + ('' if args.allow_claude else ', gpt-6-astra') + '; '
                   'efforts: low, medium, high, xhigh, max. ')
        if args.allow_claude:
            prompt += ('Claude Opus 5 workers through .benchmark-policy/scripts/claude_worker.py and the existing '
                       'Claude subscription are also authorized, including local test commands in edit profiles. '
                       'Use native C:/Users/cwbec/.local/bin/claude.exe. Read-only Claude version, auth and '
                       'inherited-context checks outside the checkout are permitted for setup. No API keys, '
                       'billing changes, paid overflow, other external agents or nested Claude delegation. '
                       'Use a receipt directory inside this checkout for Claude receipts.\n')
        else:
            prompt += 'No Claude or external agent processes in this pilot.\n'
    if args.arm == 'C':
        policy = task / '.benchmark-policy'
        policy.mkdir()
        shutil.copy2(skill_source / 'SKILL.md', policy / 'SKILL.md')
        shutil.copytree(skill_source / 'references', policy / 'references')
        if args.allow_claude:
            shutil.copytree(skill_source / 'scripts', policy / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        prompt += ('Use the agent-deployment skill at .benchmark-policy/SKILL.md for this task. '
                   'Read its references as directed. Do not modify .benchmark-policy. '
                   'If the skill cannot be read, stop and report blocked; do not perform a substitute no-skill run.\n')
    (run / 'prompt.txt').write_text(prompt, encoding='utf-8')
    command = [str(BINARY), 'exec', '--ignore-user-config', '--ignore-rules', '--strict-config',
               '--json', '--color', 'never', '-s', 'workspace-write', '-m', 'gpt-6-astra',
               '-C', str(task), *overrides, '-']
    manifest = {'arm': args.arm, 'suite': str(suite), 'task_tree': base, 'command': command, 'disabled_skills': skills,
                'source': str(source), 'python': str(runtime),
                'evaluation_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in sorted(suite.glob('*.py'))},
                'configs': configs, 'timeout_seconds': args.timeout_seconds, 'allow_claude': args.allow_claude,
                'grader': args.grader, 'grader_sha256': hashlib.sha256(grader.read_bytes()).hexdigest(),
                'base_grader_sha256': hashlib.sha256((suite / 'grade.py').read_bytes()).hexdigest(),
                'contract_sha256': hashlib.sha256(contract.read_bytes()).hexdigest() if contract else None,
                'skill_sha256': hashlib.sha256((skill_source / 'SKILL.md').read_bytes()).hexdigest(),
                'policy_sha256': {str(p.relative_to(skill_source)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(skill_source.rglob('*')) if p.is_file() and
                                  (p.name == 'SKILL.md' or p.parent.name in ('references', 'scripts')) and p.suffix in ('.md', '.py')},
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
    if args.python:
        env['PATH'] = str(runtime.parent) + os.pathsep + env.get('PATH', '')
        env['PYTHONPATH'] = str(task / 'src')
        env['FAST'] = '1'
    started = time.monotonic()
    timed_out = False
    with (run / 'events.jsonl').open('w', encoding='utf-8') as events, (run / 'stderr.log').open('w', encoding='utf-8') as errors:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=events, stderr=errors,
                                text=True, encoding='utf-8', env=env, cwd=task)
        try:
            proc.communicate(prompt, timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                           capture_output=True, timeout=20, check=True)
            proc.wait(timeout=20)
    grade = None
    grade_error = None
    if task.is_dir():
        with (run / 'grade.log').open('w', encoding='utf-8') as log:
            # Use the same sandbox identity for agent-created files; no model call.
            # Pytest's default fd capture needs temp files; sys capture stays in memory.
            grade_env = dict(env, PYTEST_ADDOPTS='--capture=sys')
            try:
                graded = subprocess.run([str(BINARY), 'sandbox', '-P', ':read-only', '-C', str(task),
                                         '-c', 'windows.sandbox="elevated"', '--', str(runtime),
                                         '-B', '-X', 'utf8', str(grader), str(task)],
                                        cwd=task, env=grade_env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
                grade = graded.returncode
            except subprocess.TimeoutExpired:
                grade_error = 'External grader timed out; run artifacts retained.'
    with (run / 'diff.patch').open('w', encoding='utf-8') as diff:
        subprocess.run(['git', '-C', str(task), 'diff'], stdout=diff, check=True)
    result = {'arm': args.arm, 'exit_code': proc.returncode, 'timed_out': timed_out,
              'seconds': round(time.monotonic() - started, 2), 'grade_exit_code': grade,
              'grade_error': grade_error,
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
