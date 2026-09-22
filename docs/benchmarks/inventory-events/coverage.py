"""Additional pre-registered inventory checks; no paid calls or reference oracle."""
import argparse
import copy
import importlib.util
import io
import json
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('original_grade', HERE / 'grade.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
event = base.event


class Coverage(unittest.TestCase):
    def test_yielded_event_mutation_does_not_rewrite_replay_history(self):
        ledger = Ledger({})
        first = event(sku='x', quantity=3)
        original = dict(first)
        def stream():
            yield first
            first['quantity'] = 99
            yield event(identity='second', sku='x', quantity=2)
        ledger.apply(stream())
        self.assertEqual(ledger.snapshot()['stock'][0]['on_hand'], 5)
        self.assertTrue(ledger.apply([original])[0]['replayed'])
        with self.assertRaises(ValueError):
            ledger.apply([first])

    def test_iterator_failure_rolls_back_each_hold_operation(self):
        for dry in (False, True):
            for prefix in (event('hold', 'p', sku='x', hold_id='new'),
                           event('ship', 'p', hold_id='h'), event('release', 'p', hold_id='h'),
                           event('transfer', 'p', sku='x', to_tenant='b')):
                ledger = Ledger({('a', 'x'): 10})
                ledger.apply([event('hold', 'seed', sku='x', hold_id='h', quantity=5)])
                before = ledger.snapshot()
                failure = RuntimeError('iterator failure')
                def broken():
                    yield prefix
                    raise failure
                with self.assertRaises(RuntimeError) as caught:
                    ledger.apply(broken(), dry_run=dry)
                self.assertIs(caught.exception, failure)
                self.assertEqual(ledger.snapshot(), before)
                self.assertEqual(ledger.apply([prefix])[0]['sequence'], 2)

    def test_replay_of_closed_hold_does_not_touch_reused_hold(self):
        for close_kind in ('ship', 'release'):
            ledger = Ledger({('a', 'x'): 10, ('a', 'y'): 9})
            opening = event('hold', 'open', sku='x', hold_id='h', quantity=3)
            closing = event(close_kind, 'close', hold_id='h', quantity=3)
            ledger.apply([opening, closing, event('hold', 'new', sku='y', hold_id='h', quantity=2)])
            before = ledger.snapshot()
            rows = ledger.apply([closing, opening, closing])
            self.assertEqual([r['sequence'] for r in rows], [2, 1, 2])
            self.assertTrue(all(r['replayed'] for r in rows))
            self.assertEqual(ledger.snapshot(), before)

    def test_failed_preview_preserves_prior_replay_receipts(self):
        ledger = Ledger({('a', 'x'): 10})
        original = event('hold', 'seed', sku='x', hold_id='h', quantity=4)
        ledger.apply([original])
        before = ledger.snapshot()
        with self.assertRaises(ValueError):
            ledger.preview([original, event('ship', 's', hold_id='h', quantity=2), {}])
        self.assertEqual(ledger.snapshot(), before)
        replay = ledger.apply([original])[0]
        self.assertEqual(replay, dict(event_id='seed', kind='hold', sequence=1, replayed=True))
        replay['replayed'] = False
        self.assertTrue(ledger.apply([original])[0]['replayed'])

    def test_deterministic_lifecycle_matrix(self):
        rng = random.Random(20260922)
        identities = ['a', ' A ', 'é', 'e\u0301', '\t', '账户']
        for case in range(80):
            a, b = rng.sample(identities, 2)
            sku = identities[case % len(identities)]
            total = rng.randrange(20, 10000)
            held = rng.randrange(3, total)
            released = rng.randrange(1, held)
            shipped = held - released
            moved = total - shipped
            ledger = Ledger({(a, sku): total})
            events = [event('hold', 'h', tenant=a, sku=sku, hold_id='lock', quantity=held),
                      event('release', 'r', tenant=a, hold_id='lock', quantity=released),
                      event('ship', 's', tenant=a, hold_id='lock', quantity=shipped),
                      event('transfer', 't', tenant=a, sku=sku, to_tenant=b, quantity=moved)]
            preview = ledger.preview(iter(events))
            self.assertEqual(ledger.snapshot()['event_count'], 0)
            self.assertEqual(ledger.apply(iter(events)), preview)
            expected = [dict(tenant=t, sku=sku, on_hand=n, held=0, available=n)
                        for t, n in sorted([(a, 0), (b, moved)])]
            self.assertEqual(ledger.snapshot(), dict(stock=expected, holds=[], event_count=4))
            self.assertTrue(all(r['replayed'] for r in ledger.apply(reversed(events))))
            self.assertEqual(ledger.snapshot(), dict(stock=expected, holds=[], event_count=4))

    def test_preview_outputs_and_snapshots_are_independent(self):
        ledger = Ledger({('a', 'x'): 5})
        events = [event('hold', 'h', sku='x', hold_id='h', quantity=2)]
        preview = ledger.preview(events)
        preview[0]['sequence'] = 900
        self.assertEqual(ledger.apply(events)[0]['sequence'], 1)
        before = copy.deepcopy(ledger.snapshot())
        snap = ledger.snapshot()
        snap['stock'].clear()
        snap['holds'].clear()
        snap['event_count'] = -1
        self.assertEqual(ledger.snapshot(), before)


def main():
    global Ledger
    p = argparse.ArgumentParser()
    p.add_argument('target', type=Path)
    p.add_argument('--protected', type=Path, required=True)
    args = p.parse_args()
    target = args.target.resolve()
    expected = json.loads(args.protected.read_text())
    bad = [n for n, h in expected.items() if not (target/n).is_file() or base.hashlib.sha256((target/n).read_bytes()).hexdigest() != h]
    if bad:
        print(json.dumps({'passed': False, 'integrity_failures': bad}))
        return 1
    sys.path.insert(0, str(target))
    from inventory import Ledger, handle
    base.Ledger, base.handle = Ledger, handle
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(base.HiddenTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(Coverage),
        unittest.defaultTestLoader.discover(str(target/'tests'), pattern='test_public.py')])
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=0).run(suite)
    print(json.dumps({'passed': result.wasSuccessful(), 'methods': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'details': output.getvalue()}))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
