import unittest
from datetime import datetime, timezone
from feed.parser import parse_csv
from retryq.queue import RetryQueue


class PublicTests(unittest.TestCase):
    def test_import(self):
        text = 'tenant,transaction_id,amount,occurred_at\na,x,1.00,2026-01-01T00:00:00Z\n'
        self.assertEqual(parse_csv(text)[0]['amount_cents'], 100)

    def test_queue(self):
        q = RetryQueue()
        q.enqueue('a', 'x', {}, datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(len(q), 1)


if __name__ == '__main__':
    unittest.main()
