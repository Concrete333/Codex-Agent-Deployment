import unittest
from inventory import Ledger, handle


class PublicTests(unittest.TestCase):
    def test_receive_and_replay(self):
        ledger = Ledger({})
        event = dict(kind='receive', event_id='r', tenant='a', sku='x', quantity=5)
        self.assertEqual(ledger.apply([event, dict(event)]), [
            dict(event_id='r', kind='receive', sequence=1, replayed=False),
            dict(event_id='r', kind='receive', sequence=1, replayed=True)])
        self.assertEqual(ledger.snapshot(), dict(stock=[dict(tenant='a', sku='x', on_hand=5, held=0, available=5)], holds=[], event_count=1))

    def test_hold_release_ship(self):
        ledger = Ledger({('a', 'x'): 10})
        ledger.apply([
            dict(kind='hold', event_id='h', tenant='a', sku='x', hold_id='h1', quantity=6),
            dict(kind='release', event_id='r', tenant='a', hold_id='h1', quantity=2),
            dict(kind='ship', event_id='s', tenant='a', hold_id='h1', quantity=4)])
        self.assertEqual(ledger.snapshot(), dict(stock=[dict(tenant='a', sku='x', on_hand=6, held=0, available=6)], holds=[], event_count=3))

    def test_atomic_failure(self):
        ledger = Ledger({('a', 'x'): 3})
        before = ledger.snapshot()
        with self.assertRaises(ValueError):
            ledger.apply([dict(kind='receive', event_id='r', tenant='a', sku='x', quantity=2),
                          dict(kind='hold', event_id='h', tenant='a', sku='x', hold_id='h', quantity=6)])
        self.assertEqual(ledger.snapshot(), before)

    def test_preview_transfer(self):
        ledger = Ledger({('a', 'x'): 5})
        event = dict(kind='transfer', event_id='t', tenant='a', to_tenant='b', sku='x', quantity=2)
        before = ledger.snapshot()
        self.assertEqual(handle(ledger, dict(events=[event], mode='preview')),
                         [dict(event_id='t', kind='transfer', sequence=1, replayed=False)])
        self.assertEqual(ledger.snapshot(), before)
        self.assertEqual(ledger.apply([event])[0]['replayed'], False)
