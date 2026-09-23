"""One selected Luna implementation and unchanged Astra acceptance."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import uuid

import three_arm as trial

POINTER = trial.HERE / 'local-luna-generation.json'
MODEL = 'gpt-6-luna'
MODELS = (MODEL, 'gpt-5.6-luna')


def prepare(model=MODEL):
    if model not in MODELS:
        raise ValueError('Unsupported comparison model')
    pointer = POINTER if model == MODEL else trial.HERE/'local-luna56-repeat.json'
    if pointer.exists():
        raise ValueError('Existing preparation retained; inspect rather than overwrite')
    prior = Path(trial.read(trial.POINTER)['root'])
    old = trial.read(prior/'manifest.json')
    cache = trial.read(Path.home()/'.codex/models_cache.json')
    metadata = next(x for x in cache['models'] if x['slug'] == model)
    assert any(x['effort'] == 'max' for x in metadata['supported_reasoning_levels'])
    root = Path(tempfile.gettempdir()) / ('inventory-' + model + '-' + uuid.uuid4().hex)
    root.mkdir()
    for name in ('source', 'policy'):
        for file in (prior/name).rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts:
                assert trial.sha(file) == old['frozen'][str(file.resolve())], str(file)
        shutil.copytree(prior/name, root/name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('protected.json', 'handoff-schema.json', 'task-contract.json', 'implement-prompt.txt', 'accept-prompt.txt'):
        assert trial.sha(prior/name) == old['frozen'][str((prior/name).resolve())], name
        shutil.copy2(prior/name, root/name)
    text = (root/'accept-prompt.txt').read_text(encoding='utf-8')
    (root/'accept-prompt.txt').write_text(text.replace(str(prior), str(root)), encoding='utf-8')
    for name in ('coverage.py', 'grade.py', 'reference.py'):
        assert trial.sha(trial.HERE/name) == old['frozen'][str((trial.HERE/name).resolve())], name
    qualification = {}
    for name, expected in old['qualification'].items():
        qualification[name] = trial.grade(root, prior/'qualification'/name, 'qualification-'+name)['passed']
        assert qualification[name] == expected, name
    binary = old['binary'] if Path(old['binary']).is_file() else trial.pair.runner.executable('codex.exe')
    for owner in ('worker', 'delegated'):
        task = root/'luna'/owner/'task'
        shutil.copytree(root/'source', task)
        for args in (['git', 'init', '-q'], ['git', 'config', 'core.autocrlf', 'false'], ['git', 'add', '.'],
                     ['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@invalid',
                      'commit', '-qm', 'frozen inventory input']):
            proc = trial.pair.call(args, task)
            assert proc.returncode == 0, proc.stderr
        trial.pair.runner.preflight(binary, {'provider': 'codex', 'profile': 'edit', 'cwd': str(task)},
                                   trial.pair.runner.worker_env('codex'))
    m = {k: old[k] for k in ('config', 'model', 'effort', 'sol_timeout_seconds', 'rates_per_million')}
    m['rates_per_million'][MODEL] = [.1, .01, .125, .5]
    m.update(root=str(root), prior_root=str(prior), binary=binary, luna_model=model,
             thread=os.environ['CODEX_THREAD_ID'], order=['luna'], maximum_sessions=2,
             automatic_retry=False, qualification=qualification,
             codex_version=trial.pair.call([binary, '--version'], root).stdout.strip(),
             prior_codex_version=old['codex_version'],
             pricing_source='https://developers.openai.com/api/docs/pricing', pricing_date='2026-09-23')
    trial.save(root/'requested-model.json', {'slug': metadata['slug'],
        'supported_reasoning_levels': metadata['supported_reasoning_levels']})
    frozen = [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    frozen += [Path(__file__), trial.HERE/'three_arm.py', trial.HERE/'coverage.py', trial.HERE/'grade.py',
               trial.HERE/'reference.py', Path(trial.pair.__file__), trial.REPO/'scripts/deployment_runner.py',
               trial.REPO/'scripts/claude_worker.py']
    m['frozen'] = {str(p.resolve()): trial.sha(p) for p in frozen}
    trial.save(root/'manifest.json', m)
    trial.save(pointer, {'root': str(root)})
    trial.save(root/'notify-request.json', {'codex': binary, 'thread': m['thread'], 'cwd': str(trial.REPO),
        'argv': [sys.executable, '-B', str(Path(__file__).resolve()), 'run', '--root', str(root)],
        'receipt': str(root/'result.json')})
    print(json.dumps({'prepared': str(root), 'model': model, 'effort': 'max', 'paid_calls': 0,
                      'qualification': qualification, 'cli': m['codex_version'], 'prior_cli': old['codex_version']}))


def run(root):
    m = trial.read(root/'manifest.json')
    assert m['luna_model'] in MODELS and m['maximum_sessions'] == 2
    assert all(trial.sha(p) == h for p, h in m['frozen'].items()), 'Frozen input changed'
    with (root/'started.json').open('x') as stream:
        json.dump({'started_at': time.time()}, stream)
    trial.save(root/'result.json', {'status': 'running', 'arms': {}, 'maximum_sessions': 2})
    arm = trial.run_arm(root, m, 'luna')
    result = {'status': 'finished' if arm['status'] == 'finished' else 'needs_attention',
              'arms': {'luna': arm}, 'maximum_sessions': 2, 'automatic_retry': False}
    trial.save(root/'result.json', result)
    print(json.dumps(result))
    return 0 if result['status'] == 'finished' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run'])
    parser.add_argument('--root', type=Path)
    parser.add_argument('--model', choices=MODELS, default=MODEL)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.model)
    else:
        if args.root is None:
            parser.error('run requires --root')
        raise SystemExit(run(args.root))
