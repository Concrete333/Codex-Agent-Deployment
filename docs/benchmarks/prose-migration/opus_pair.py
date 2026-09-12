"""Prepare/run two isolated Opus Low diagnostics through the existing wrapper."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from experiment import save
from review_only import PROMPT, frozen

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main(mode):
    fixture = json.loads((HERE / 'local-fixture.json').read_text())
    original = Path(fixture['root'])
    root = original / 'opus-pair'
    wrapper = REPO / 'scripts/claude_worker.py'
    if mode == 'prepare':
        root.mkdir(exist_ok=False)
        jobs = []
        for role in ('builder', 'reviewer'):
            task = root / role
            task.mkdir()
            shutil.copy2(Path(fixture['source']) / 'TASK.md', task / 'TASK.md')
            shutil.copytree(Path(fixture['source']) / 'threads', task / 'threads')
            if role == 'reviewer':
                shutil.copy2(original / 'sol-review/task/answer.json', task / 'answer.json')
                fingerprint = hashlib.sha256((task / 'answer.json').read_bytes()).hexdigest()
                assert fingerprint == '8842b97ada5925862d1b88d5c934199286e3c237168c0096edd8560697610d1f'
                prompt = PROMPT + ('\nYour tools are read-only Read/Glob/Grep; report executable checks you cannot run. '
                                   'The evaluator will run structural checks separately. '
                                   'Input answer SHA-256 supplied by the harness: ' + fingerprint + '.\n')
            else:
                prompt = ('Complete TASK.md using only this checkout. Own the entire answer, self-checks and corrections. '
                          'Write answer.json and verify it against the original discussions and task requirements. '
                          'Do not inspect other trials, personal memory, skills, logs or repositories; no web, delegation '
                          'or external model calls. These discussions are primary evidence; read their exact text without '
                          'lossy summarization. Local scripts and test commands within this checkout are permitted. '
                          'Do not change TASK.md or threads/. Return the answer path, checks and unresolved work concisely. '
                          'Python executable: ' + fixture['python'] + '.')
            jobs.append({'id': role, 'model': 'claude-opus-5', 'effort': 'low',
                         'profile': 'edit' if role == 'builder' else 'review',
                         'allow_shell': role == 'builder', 'trusted_context': True,
                         'cwd': str(task), 'timeout_seconds': 2700, 'max_budget_usd': 5, 'prompt': prompt})
        save(root / 'request.json', {'max_concurrent': 1, 'jobs': jobs})
        manifest = {'inputs': {role: frozen(root / role) for role in ('builder', 'reviewer')},
                    'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__), wrapper, root / 'request.json', REPO / 'SKILL.md')},
                    'note': 'Worker-only tests, separate sessions; no prior findings or gold supplied. Reviewer has no shell.'}
        save(root / 'manifest.json', manifest)
        check = subprocess.run([sys.executable, '-B', str(wrapper), str(root / 'request.json'), '--dry-run'],
                               cwd=REPO, capture_output=True, text=True, encoding='utf-8')
        (root / 'preflight.json').write_text(check.stdout + check.stderr, encoding='utf-8')
        assert check.returncode == 0, check.stdout + check.stderr
        print(json.dumps({'prepared': str(root), 'jobs': [j['id'] for j in jobs], 'preflight': 'passed'}))
        return
    manifest = json.loads((root / 'manifest.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in manifest['sha256'].items())
    assert all(frozen(root / role) == hashes for role, hashes in manifest['inputs'].items())
    with (root / 'started.json').open('x') as marker:
        json.dump({'jobs': ['builder', 'reviewer']}, marker)
    print('Running Opus Low builder then independent reviewer; no automatic retries.', flush=True)
    with (root / 'batch-result.json').open('w', encoding='utf-8') as log:
        proc = subprocess.run([sys.executable, '-B', str(wrapper), str(root / 'request.json'),
                               '--receipt-dir', str(root)], cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
    print((root / 'batch-result.json').read_text(encoding='utf-8'), flush=True)
    raise SystemExit(proc.returncode)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('prepare', 'run'):
        raise SystemExit('Usage: opus_pair.py prepare|run')
    main(sys.argv[1])
