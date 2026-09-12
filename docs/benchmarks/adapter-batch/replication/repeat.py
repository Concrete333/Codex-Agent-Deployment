"""Repeat the frozen first pair without replacing its inputs or receipts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('adapter_experiment', HERE.parent / 'experiment.py')
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)


def fixtures():
    original = experiment.shared.load()
    old_root = Path(original['root'])
    approved = json.loads((old_root / 'preflight.json').read_text(encoding='utf-8'))
    assert approved['passed'] and approved['frozen'] == experiment.frozen(original), 'Original freeze changed'
    plan = json.loads((old_root / 'run-plan.json').read_text(encoding='utf-8'))
    assert len(plan['runs']) == 2 and all(r['result'] for r in plan['runs']), 'First pair incomplete'
    repeated = {**original, 'root': str(old_root / 'replication-02')}
    return original, repeated


def verify(original, repeated):
    old_root, new_root = Path(original['root']), Path(repeated['root'])
    expected = experiment.frozen(original)
    expected[str(new_root / 'held-out.json')] = expected.pop(str(old_root / 'held-out.json'))
    assert expected == experiment.frozen(repeated), 'Repeated inputs differ'
    record = json.loads((new_root / 'replication.json').read_text(encoding='utf-8'))
    assert record['driver_sha256'] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'Repeat driver changed'


def prepare(original, repeated):
    root = Path(repeated['root'])
    root.mkdir(exist_ok=False)
    shutil.copy2(Path(original['root']) / 'held-out.json', root / 'held-out.json')
    experiment.shared.save(root / 'replication.json', {
        'replicates': original['root'], 'order': ['A', 'C'],
        'public_label_for_C': 'D: required Luna Max',
        'changed_conditions': [],
        'note': 'New receipt directory and fresh participant checkouts; original source, policy, runner and grading cases reused.',
        'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    })
    verify(original, repeated)
    experiment.preflight(repeated)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'run', 'summarize'))
    args = parser.parse_args()
    original, repeated = fixtures()
    if args.operation == 'prepare':
        prepare(original, repeated)
    else:
        verify(original, repeated)
        getattr(experiment.shared, args.operation)(repeated)
