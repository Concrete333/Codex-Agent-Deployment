"""Qualified old/new skill comparison; both arms require one Luna Max worker."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

from boundaries_hidden import cases as hidden_cases
from boundaries_visible import cases as visible_cases

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('adapter_experiment', HERE.parent / 'experiment.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
shared = base.shared
original = shared.load()
original_hashes = base.frozen(original)
assert json.loads((Path(original['root']) / 'preflight.json').read_text())['frozen'] == original_hashes
base.HERE = shared.HERE = HERE


def frozen(fixture):
    paths = list(HERE.glob('*.py')) + [Path(fixture['runner']), Path(fixture['root']) / 'held-out.json',
             HERE.parent / 'experiment.py', HERE.parent / 'grade.py',
             shared.REPO / 'docs/benchmarks/checked-component/experiment.py',
             shared.REPO / 'docs/benchmarks/revision-ab/summarize.py']
    for field in ('source', 'policy', 'old_policy', 'reference'):
        paths += list(Path(fixture[field]).rglob('*'))
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


def command(fixture, arm, prepare=False):
    # Internal A means old policy, C means new policy. Both invoke the original
    # runner's required-delegation C workflow; there is no solo participant here.
    cmd = [fixture['python'], '-B', '-X', 'utf8', fixture['runner'], 'C',
           '--suite', str(HERE), '--source', fixture['source'], '--python', fixture['python'],
           '--skill-source', fixture['old_policy'] if arm == 'A' else fixture['policy'],
           '--timeout-seconds', '1200']
    return cmd + ['--prepare-only'] if prepare else cmd


base.frozen = shared.frozen = frozen
shared.command = command


def prepare():
    local = HERE / 'local-fixture.json'
    assert not local.exists(), 'Preserve previous fixture and receipt identities'
    root = Path(tempfile.gettempdir()) / ('agent-deployment-selection-' + uuid.uuid4().hex)
    root.mkdir(exist_ok=False)
    source, reference = root / 'source', root / 'reference'
    shutil.copytree(original['source'], source)
    shutil.copy2(HERE / 'boundaries_visible.py', source / 'boundaries_visible.py')
    checker = source / 'check_contract.py'
    text = checker.read_text(encoding='utf8')
    marker = "    cases = json.loads(cases_path.read_text(encoding='utf-8'))"
    assert text.count(marker) == 1
    text = text.replace(marker, marker + "\n    if cases_path.name == 'fixtures.json':\n        from boundaries_visible import cases as boundary_cases\n        cases += boundary_cases()")
    checker.write_text(text, encoding='utf8')
    task = source / 'TASK.md'
    task.write_text(task.read_text(encoding='utf8') + '\nThe supplied checker also runs compact generated boundary cases from `boundaries_visible.py`. That file is protected; run `python -B check_contract.py` for the complete visible suite.\n', encoding='utf8')
    owned = {'imports/adapters/' + fmt + '.py' for fmt in original['formats']}
    manifest = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.rglob('*') if p.is_file() and p.name != 'protected_hashes.json'
                and p.relative_to(source).as_posix() not in owned}
    shared.save(source / 'protected_hashes.json', manifest)
    shutil.copytree(original['reference'], reference)
    for rel in list(manifest) + ['protected_hashes.json']:
        shutil.copy2(source / rel, reference / rel)
    shutil.copy2(HERE / 'reference_csv.py', reference / 'imports/adapters/_shared.py')
    for name in ('bank_csv.py', 'euro_csv.py'):
        path = reference / 'imports/adapters' / name
        content = path.read_text(encoding='utf8')
        assert content.count('reader = csv.reader(') == 1
        content = content.replace('from .. import common', 'from .. import common\nfrom . import _shared')
        content = content.replace('reader = csv.reader(', 'reader = _shared.reader(')
        path.write_text(content, encoding='utf8')
    held_out = json.loads((Path(original['root']) / 'held-out.json').read_text()) + hidden_cases()
    shared.save(root / 'held-out.json', held_out)
    shutil.copytree(original['policy'], root / 'old-policy')
    shutil.copytree(original['policy'], root / 'policy')
    shutil.copy2(shared.REPO / 'SKILL.md', root / 'policy/SKILL.md')
    fixture = {**original, 'root': str(root), 'source': str(source), 'reference': str(reference),
               'old_policy': str(root / 'old-policy'), 'policy': str(root / 'policy'),
               'python': sys.executable}
    shared.save(local, fixture)
    shared.save(root / 'design.json', {'old_fixture': original['root'], 'original_hashes': original_hashes,
                'arms': {'A': 'old skill, required Luna Max', 'C': 'conditional-read skill, required Luna Max'},
                'public_cases': 140 + len(visible_cases()), 'held_out_cases': len(held_out),
                'single_policy_change': 'Skip model selection only when model and effort are fixed',
                'order': ['A', 'C'], 'automatic_retry': False})
    print(json.dumps({'prepared': str(root), 'public_cases': 140 + len(visible_cases()), 'held_out_cases': len(held_out)}))


def preflight(fixture):
    root = Path(fixture['root'])
    assert not (root / 'started.json').exists()
    # The previously missed library limit must now fail qualification.
    target = root / ('legacy-limit-' + uuid.uuid4().hex[:8])
    shutil.copytree(fixture['reference'], target)
    for name in ('bank_csv.py', 'euro_csv.py'):
        path = target / 'imports/adapters' / name
        path.write_text(path.read_text().replace('reader = _shared.reader(', 'reader = csv.reader('), encoding='utf8')
    done = subprocess.run([fixture['python'], '-B', '-X', 'utf8', str(HERE / 'grade.py'), str(target)],
                          capture_output=True, text=True, encoding='utf8', timeout=180)
    shared.save(root / 'legacy-limit-rejection.json', {'exit_code': done.returncode, 'stdout': done.stdout, 'stderr': done.stderr})
    assert done.returncode != 0, 'Legacy field limit was not detected'
    base.preflight(fixture)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'preflight', 'run', 'summarize'))
    args = parser.parse_args()
    if args.operation == 'prepare':
        prepare()
    elif args.operation == 'preflight':
        preflight(shared.load())
    else:
        getattr(shared, args.operation)(shared.load())
