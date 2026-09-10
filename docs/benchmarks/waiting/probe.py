"""One paid waiting-only probe, using a trusted prior benchmark manifest.

No routing skill, repo exploration or full coding benchmark. Raw receipts stay
in a unique temporary directory. Never execute an untrusted command manifest.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


PROMPT = '''This is an authorized, bounded runtime waiting test, not a coding task.
Keep your current model and effort. Do not read files, skills, logs or repositories,
use the network, or change configuration. Check your callable tool definitions:
is there an interruptible native worker-completion wait you can use consistently
with higher-priority responsiveness instructions? A textual mention is not a tool.
If no such wait is callable or allowed, do not spawn anything: return BLOCKED and
the missing control. Do not substitute clocks, shell sleeps, status polling,
automations, or a wrapper for the parent's completion wait.

If the wait is available, spawn exactly one worker with model gpt-5.6-luna,
reasoning_effort max and fork_turns none. Give this complete assignment:
"In the supplied temporary working directory, use one shell command to run
python -B -c \\"import time; time.sleep(40); print('WAIT_PROBE_DONE')\\".
This is a waiting test; do not inspect files, make edits or delegate. Await that
single command within host limits, then return only WAIT_PROBE_DONE or its exact
failure."
Use the native completion wait until its result arrives, respecting host limits.
Do not inspect status after an empty timeout or send redundant worker messages.
Report the actual wait tool, completion result and any limitation in <=100 words.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, help='Trusted local C2 manifest.json')
    args = parser.parse_args()
    source = json.loads(args.manifest.read_text(encoding='utf-8'))
    command = list(source['command'])
    if Path(command[0]).name != 'codex.exe' or command[1] != 'exec' or command[-1] != '-':
        parser.error('Expected the existing Codex exec benchmark command')
    run = Path(tempfile.mkdtemp(prefix='agent-deployment-waiting-'))
    task = run / 'task'
    task.mkdir()
    subprocess.run(['git', 'init', '-q', str(task)], check=True)
    command[command.index('-C') + 1] = str(task)
    (run / 'prompt.txt').write_text(PROMPT, encoding='utf-8')
    (run / 'manifest.json').write_text(json.dumps({
        'source_manifest': str(args.manifest.resolve()), 'command': command,
        'timeout_seconds': 180, 'parent_model': source['parent_model'],
        'parent_effort': source['parent_effort'], 'configs': source['configs'],
    }, indent=2), encoding='utf-8')
    print(json.dumps({'run_directory': str(run)}), flush=True)
    env = dict(os.environ)
    for name in ('OPENAI_API_KEY', 'CODEX_API_KEY'):
        env.pop(name, None)
    env['PYTHONUTF8'] = '1'
    started, timed_out = time.monotonic(), False
    with (run / 'events.jsonl').open('w', encoding='utf-8') as events, \
            (run / 'stderr.log').open('w', encoding='utf-8') as errors:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=events,
                                stderr=errors, cwd=task, env=env, text=True, encoding='utf-8')
        try:
            proc.communicate(PROMPT, timeout=180)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                           check=True, capture_output=True, timeout=20)
            proc.wait(timeout=20)
    result = dict(exit_code=proc.returncode, timed_out=timed_out,
                  seconds=round(time.monotonic() - started, 2), run_directory=str(run))
    (run / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
