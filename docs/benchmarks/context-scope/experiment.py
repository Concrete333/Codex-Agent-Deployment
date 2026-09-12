"""Frozen worker-packet ablation on source inventories. prepare is offline; run spends."""
import argparse
import ast
from collections import Counter
import importlib.util
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
sys.path.insert(0, str(REPO / 'scripts'))
import deployment_runner as runner

BINARY = Path.home() / 'AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
POINTER = HERE / 'local-fixture.json'
SOURCE = Path('C:/Users/cwbec/Spaceships')
TASKS = {
    'fees': ['store_credit_value', 'sh_fee_rate', 'paypal_fee_rate', 'paypal_fixed_fee',
             'lti_min_profit_cost_rate', 'ten_year_min_profit_cost_rate', 'ccu_min_profit_cost_rate'],
    'funding': ['melt_grace_minutes', 'ccu_melt_grace_minutes', 'ccu_credit_reserve',
                'ccu_cart_item_limit', 'ccu_cart_per_target'],
}
TREATMENT = ('Context handling: Discover candidate files within the relevant paths and file types before '
             'reading bodies; exclude unrelated generated or captured content. Read matching functions or '
             'ranges. If output truncates, recover the missing relevant ranges instead of treating the '
             'partial return as complete. Widen the search when evidence or coverage requires it.')
save = runner.atomic_json


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def hashes(root):
    return {p.relative_to(root).as_posix(): runner.hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}


def expected(root, keys):
    rows = []
    for path in sorted((root / 'src').glob('*.py')):
        text = path.read_text(encoding='utf-8-sig')
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == 'get' and node.args and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value in keys):
                rows.append({'path': path.relative_to(root).as_posix(), 'line': node.lineno,
                             'key': node.args[0].value, 'expression': ast.get_source_segment(text, node)})
    return rows


def normalized(rows):
    result = []
    if not isinstance(rows, list):
        raise ValueError('Expected a JSON array')
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'path', 'line', 'key', 'expression'}:
            raise ValueError('Wrong inventory row schema')
        if type(row['line']) is not int or not all(isinstance(row[k], str) for k in ('path', 'key', 'expression')):
            raise ValueError('Wrong inventory field types')
        expr = ast.dump(ast.parse(row['expression'].strip(), mode='eval'), include_attributes=False)
        result.append((row['path'], row['line'], row['key'], expr))
    return Counter(result)


def grade(task, gold):
    changes = [name for name, digest in gold['corpus'].items()
               if not (task / name).is_file() or runner.hashlib.sha256((task / name).read_bytes()).hexdigest() != digest]
    if changes:
        return {'accepted': False, 'reason': 'protected corpus changed', 'files': changes}
    try:
        actual, wanted = normalized(read(task / 'inventory.json')), normalized(gold['rows'])
    except (OSError, ValueError, SyntaxError, TypeError) as exc:
        return {'accepted': False, 'reason': str(exc)}
    return {'accepted': actual == wanted, 'expected_rows': sum(wanted.values()),
            'actual_rows': sum(actual.values()), 'missing': sum((wanted - actual).values()),
            'extra_or_wrong': sum((actual - wanted).values())}


def sandbox(task, argv):
    return [str(BINARY), 'sandbox', '-P', ':read-only', '-C', str(task),
            '-c', 'windows.sandbox="elevated"', '--', *map(str, argv)]


def prepare():
    if POINTER.exists():
        raise ValueError('Existing frozen fixture; do not overwrite or silently repeat')
    root = Path(tempfile.mkdtemp(prefix='deployment-context-scope-')).resolve()
    corpus = root / 'corpus'
    corpus.mkdir()
    # Source text only. No databases, raw captures, secrets/configuration, profiles or historical plans.
    for subdir, sources in [('src', sorted(SOURCE.glob('*.py')) + sorted(SOURCE.glob('*.js'))),
                            ('tests', sorted((SOURCE / 'tests').glob('test_*.py')) + sorted((SOURCE / 'tests').glob('*.js')))]:
        (corpus / subdir).mkdir()
        for path in sources:
            shutil.copy2(path, corpus / subdir / path.name)
    (corpus / 'AGENTS.md').write_text('This is a source-only research checkout. Do not import or execute its application code. '
        'Read only this checkout. Do not access the original project, sibling trials, private graders or personal context. '
        'No network, package installation, other agents or background work. Preserve src/ and tests/ unchanged. '
        'Write only inventory.json and optional scratch scripts in .audit-work/.\n', encoding='utf-8')
    corpus_hashes = hashes(corpus)
    save(corpus / 'corpus.sha256.json', corpus_hashes)
    old = read(REPO / 'docs/benchmarks/runner-comparison/local-fixture.json')
    state = Path(read(Path(old['root']) / 'manifest.json')['state'])
    if (state / 'active.json').exists():
        raise ValueError('Existing runner has unresolved ownership; no new trial')
    shutil.copy2(REPO / 'references/delegation.md', root / 'baseline-delegation.md')
    (root / 'candidate-worker-instruction.txt').write_text(TREATMENT, encoding='utf-8')
    runs = []
    for task_name, order in [('fees', ['A', 'B']), ('funding', ['B', 'A'])]:
        gold = {'rows': expected(corpus, TASKS[task_name]), 'corpus': corpus_hashes}
        assert gold['rows'], task_name
        # Qualify complete, missing, duplicate, wrong-expression and wrong-location artifacts before spending.
        qualification = root / ('qualify-' + task_name)
        shutil.copytree(corpus, qualification)
        save(qualification / 'inventory.json', gold['rows'])
        assert grade(qualification, gold)['accepted']
        mutants = [[], gold['rows'][:-1], gold['rows'] + gold['rows'][:1],
                   [{**gold['rows'][0], 'expression': 'None'}, *gold['rows'][1:]],
                   [{**gold['rows'][0], 'line': gold['rows'][0]['line'] + 1}, *gold['rows'][1:]]]
        for mutant in mutants:
            save(qualification / 'inventory.json', mutant)
            assert not grade(qualification, gold)['accepted']
        save(qualification / 'inventory.json', gold['rows'])
        save(root / (task_name + '-gold.json'), gold)
        preflight = subprocess.run(sandbox(qualification, [sys.executable, '-B', str(HERE / 'experiment.py'),
                'grade', '--task', str(qualification), '--keys', json.dumps(TASKS[task_name])]),
                capture_output=True, text=True, encoding='utf-8', timeout=90)
        save(root / (task_name + '-preflight.json'), {'exit_code': preflight.returncode, 'stdout': preflight.stdout, 'stderr': preflight.stderr})
        assert preflight.returncode == 0, preflight.stderr
        for arm in order:
            label = task_name + '-' + arm
            folder = root / label
            task = folder / 'task'
            shutil.copytree(corpus, task)
            subprocess.run(['git', 'init', '-q', str(task)], check=True)
            contract = ('Produce a complete source inventory for the following literal keys: ' + ', '.join(TASKS[task_name]) + '.\n'
                'Inventory every Python .get(...) call in production src/ whose first positional argument is exactly one '
                'of those string literals. Include nested functions and any receiver; exclude comments, string contents, '
                'dictionary definitions, subscripts, dynamic keys and tests/ callers. Do not infer equivalent keys or behavior.\n'
                'Write inventory.json as a JSON array. Each row has exactly path (relative POSIX path), line (one-based '
                'line where that call starts), key (literal string) and expression (the complete original call expression, '
                'including receiver and arguments). Preserve Python semantics; whitespace may differ. Include all matching '
                'calls exactly once, including multiple matches on a line. Row order does not matter.\n'
                'This is extraction, not an economic policy review or implementation change. You may use scripts to obtain '
                'a complete result. A grader outside your scope checks every row and source integrity. Read AGENTS.md.\n')
            (task / 'TASK.md').write_text(contract, encoding='utf-8')
            prompt = ('Complete TASK.md. Own the inventory and local development checks. Relevant evidence is the source-only '
                      'checkout, with production in src/ and test material in tests/. The host owns the final inventory '
                      'check. Do not read outside this checkout.\n')
            if arm == 'B':
                prompt += TREATMENT + '\n'
            job = runner.validate({'id': 'context-' + label.lower(), 'provider': 'codex', 'model': 'gpt-5.6-luna',
                'effort': 'max', 'profile': 'edit', 'cwd': str(task), 'trusted_context': True,
                'timeout_seconds': 900, 'prompt': prompt, 'artifacts': ['inventory.json'],
                'protected_files': ['AGENTS.md', 'TASK.md', 'corpus.sha256.json'],
                'checks': [{'id': 'complete-inventory', 'argv': [sys.executable, '-B', str(HERE / 'experiment.py'),
                            'grade', '--task', str(task), '--keys', json.dumps(TASKS[task_name])], 'timeout_seconds': 60}]})
            save(folder / 'request.json', job)
            runs.append({'task': task_name, 'arm': arm, 'folder': str(folder), 'request': str(folder / 'request.json')})
    frozen = {str(p): runner.hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),
              REPO / 'scripts/deployment_runner.py', REPO / 'scripts/deployment_hash.py', REPO / 'scripts/claude_worker.py',
              REPO / 'docs/benchmarks/revision-ab/summarize.py', root / 'baseline-delegation.md', root / 'candidate-worker-instruction.txt']}
    for run in runs:
        folder = Path(run['folder'])
        for name, digest in hashes(folder).items():
            frozen[str(folder / name)] = digest
    for task_name in TASKS:
        p = root / (task_name + '-gold.json')
        frozen[str(p)] = runner.hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = {'root': str(root), 'state': str(state), 'runs': runs, 'frozen': frozen,
                'rows': {k: len(expected(corpus, v)) for k, v in TASKS.items()}, 'source_files': len(corpus_hashes),
                'source_bytes': sum((corpus / n).stat().st_size for n in corpus_hashes),
                'model': 'gpt-5.6-luna', 'effort': 'max', 'paid_runs': 4, 'automatic_retry': False,
                'scope': 'Worker-packet mechanism test; no model coordinator, no autonomous dispatch, no complete implementation.'}
    save(root / 'manifest.json', manifest)
    save(POINTER, {'root': str(root)})
    print(json.dumps({k: manifest[k] for k in ('root', 'rows', 'source_files', 'source_bytes', 'scope')}))


def run_all():
    root = Path(read(POINTER)['root'])
    manifest = read(root / 'manifest.json')
    assert all(runner.hashlib.sha256(Path(p).read_bytes()).hexdigest() == sha for p, sha in manifest['frozen'].items())
    with (root / 'started.json').open('x') as stream:
        json.dump({'time': time.time(), 'runs': 4}, stream)
    for item in manifest['runs']:
        folder = Path(item['folder'])
        job = read(item['request'])
        print(json.dumps({'stage': 'starting', 'task': item['task'], 'arm': item['arm']}), flush=True)
        receipt = runner.run(job, Path(manifest['state']), str(BINARY))
        save(folder / 'result.json', receipt)
        print(json.dumps({'stage': 'finished', 'task': item['task'], 'arm': item['arm'], 'status': receipt['status']}), flush=True)
        if receipt.get('ownership_check_required') or (Path(manifest['state']) / 'active.json').exists():
            raise RuntimeError('Stopped after unresolved ownership; no successor launched')
    summarize()


def summarize():
    root = Path(read(POINTER)['root'])
    manifest = read(root / 'manifest.json')
    spec = importlib.util.spec_from_file_location('accounting', REPO / 'docs/benchmarks/revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    index = accounting.session_index()
    report = {'scope': manifest['scope'], 'rates': accounting.RATES,
              'caveat': 'Frozen historical API-equivalent rates, not current price or allowance. Research preparation, supervision and external grading excluded.', 'runs': []}
    for item in manifest['runs']:
        path = Path(item['folder']) / 'result.json'
        if not path.exists():
            continue
        receipt = read(Path(manifest['state']) / read(item['request'])['id'] / 'receipt.json')
        tid = receipt.get('worker', {}).get('session_id')
        if not tid:
            tid = runner.interrupted_codex_session(receipt['worker_process']['stdout_path'])
        result = accounting.audit_thread(tid, index[tid]) if tid in index else {'error': 'Missing own-session usage'}
        if result.get('reconciled'):
            assert result['configurations'] == [('gpt-5.6-luna', 'max')], result['configurations']
        row = {**item, 'status': receipt['status'], 'accounting': result, 'checks': receipt.get('checks', []),
               'seconds': receipt.get('worker_process', {}).get('duration_seconds')}
        report['runs'].append(row)
        print(json.dumps({'task': row['task'], 'arm': row['arm'], 'status': row['status'], 'seconds': row['seconds'],
              'cost': result.get('api_equivalent_usd'), 'usage': result.get('usage'), 'responses': result.get('responses'),
              'reconciled': result.get('reconciled')}), flush=True)
    save(root / 'accounting.json', report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'run', 'summarize', 'grade'])
    parser.add_argument('--task', type=Path)
    parser.add_argument('--gold', type=Path)
    parser.add_argument('--keys')
    args = parser.parse_args()
    if args.operation == 'grade':
        gold = read(args.gold) if args.gold else {'rows': expected(args.task, json.loads(args.keys)),
                                                'corpus': read(args.task / 'corpus.sha256.json')}
        result = grade(args.task, gold)
        print(json.dumps(result))
        raise SystemExit(0 if result['accepted'] else 1)
    {'prepare': prepare, 'run': run_all, 'summarize': summarize}[args.operation]()
