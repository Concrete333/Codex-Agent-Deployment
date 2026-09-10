"""V1 checks plus independent boundary/state checks; see grading-v2.md.

Usage: python grade_v2.py --reference -q
       python grade_v2.py PATH_TO_SAVED_TASK -q
"""
import random
import unittest
from datetime import datetime, timedelta, timezone, tzinfo
from decimal import localcontext
from email.utils import format_datetime

# V1 selects the target from argv. Keep its checks and file unchanged.
import grade as v1
from grade import FeedChecks, RetryChecks


class OffsetShift(tzinfo):
    """A deterministic clock change; no installed timezone database required."""

    def __init__(self, before, after):
        self.before, self.after = before, after

    def utcoffset(self, value):
        return timedelta(hours=self.before if value.hour < 2 else self.after)

    def dst(self, value):
        return timedelta(0)


class BoundaryChecks(unittest.TestCase):
    def test_elapsed_delay_across_clock_changes(self):
        for before, after in ((1, 2), (2, 1)):
            with self.subTest(before=before, after=after):
                now = datetime(2026, 3, 29, 1, 59, 59, tzinfo=OffsetShift(before, after))
                expected = now.astimezone(timezone.utc) + timedelta(seconds=2)
                queue = v1.RetryQueue()
                v1.RetryService(queue).fail('a', 'x', {}, 1, now, 500, base=2)
                self.assertEqual(queue.pop_due(expected - timedelta(microseconds=1)), [])
                jobs = queue.pop_due(expected)
                self.assertEqual(len(jobs), 1)
                self.assertEqual(jobs[0]['due_at'], expected)
                self.assertEqual(jobs[0]['due_at'].utcoffset(), timedelta(0))

    def test_http_date_elapsed_time_across_clock_change(self):
        now = datetime(2026, 3, 29, 1, 59, 59, tzinfo=OffsetShift(1, 2))
        expected = now.astimezone(timezone.utc) + timedelta(seconds=3)
        header = format_datetime(expected, usegmt=True)
        self.assertEqual(v1.retry_delay(1, now, retry_after=header), 3)
        queue = v1.RetryQueue()
        v1.RetryService(queue).fail('a', 'x', {}, 1, now, 429, retry_after=header)
        self.assertEqual(queue.pop_due(expected)[0]['due_at'], expected)

    def test_equal_instants_and_microsecond_boundaries(self):
        queue = v1.RetryQueue()
        for identity, offset in [('first', 14), ('second', -7)]:
            queue.enqueue('a', identity, {}, v1.NOW.astimezone(timezone(timedelta(hours=offset))))
        self.assertEqual(queue.pop_due(v1.NOW - timedelta(microseconds=1)), [])
        self.assertEqual([job['job_id'] for job in queue.pop_due(v1.NOW)], ['first', 'second'])

    def test_fractional_seconds_and_float_extremes(self):
        cases = [(1, .125, 60, .125), (4, .125, .75, .75),
                 (100000, 1e-300, 60, 60), (100000, 1e300, 60, 60)]
        for attempt, base, cap, expected in cases:
            with self.subTest(attempt=attempt, base=base, cap=cap):
                self.assertAlmostEqual(float(v1.retry_delay(attempt, v1.NOW, base=base, cap=cap)), expected)
        queue = v1.RetryQueue()
        v1.RetryService(queue).fail('a', 'x', {}, 1, v1.NOW, 500, base=.125)
        self.assertEqual(queue.pop_due(v1.NOW + timedelta(microseconds=124999)), [])
        self.assertEqual(queue.pop_due(v1.NOW + timedelta(microseconds=125000))[0]['due_at'],
                         v1.NOW + timedelta(microseconds=125000))

    def test_invalid_limits_preserve_existing_job(self):
        for params in ({'base': float('nan')}, {'cap': float('inf')}, {'base': -0.125}):
            with self.subTest(params=params):
                queue = v1.RetryQueue()
                queue.enqueue('a', 'x', {'original': True}, v1.NOW)
                with self.assertRaises(ValueError):
                    v1.RetryService(queue).fail('a', 'x', {'replacement': True}, 1, v1.NOW, 503, **params)
                self.assertEqual(queue.pop_due(v1.NOW)[0]['payload'], {'original': True})

    def test_exact_money_ignores_ambient_precision(self):
        for precision in (6, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                records = v1.parse_csv(v1.document([v1.row(amount='999999999.990000000000000000000')]))
                self.assertEqual(records[0]['amount_cents'], 99999999999)

    def test_distant_fractional_cent_is_rejected_atomically(self):
        store = v1.Store()
        with self.assertRaises(ValueError):
            v1.ImportService(store).import_csv(v1.document([
                v1.row('valid'), v1.row('invalid', amount='1.00000000000000000000000000001')]))
        self.assertEqual(store.calls, [])

    def test_signed_money_boundaries(self):
        for amount, expected in [('1000000000.00', 100000000000),
                                 ('-1000000000.00', -100000000000), ('-0.0000', 0)]:
            with self.subTest(amount=amount):
                self.assertEqual(v1.parse_csv(v1.document([v1.row(amount=amount)]))[0]['amount_cents'], expected)

    def test_seeded_queue_sequences(self):
        # A list-based specification: replacement keeps a slot; removal destroys it.
        # Never use the reference implementation to calculate expected results.
        for seed in (7, 29, 83):
            rng = random.Random(seed)
            queue, expected = v1.RetryQueue(), []
            for step in range(80):
                with self.subTest(seed=seed, step=step):
                    if rng.random() < .65:
                        tenant, identity = rng.choice(('a', 'b')), str(rng.randrange(5))
                        due = v1.NOW + timedelta(seconds=rng.randrange(6))
                        record = dict(tenant=tenant, job_id=identity, payload={'step': [step]}, due_at=due)
                        slot = next((i for i, old in enumerate(expected)
                                     if (old['tenant'], old['job_id']) == (tenant, identity)), len(expected))
                        payload = {'step': [step]}
                        queue.enqueue(tenant, identity, payload, due.astimezone(timezone(timedelta(hours=-4))))
                        payload['step'].append('mutated')
                        if slot == len(expected):
                            expected.append(record)
                        else:
                            expected[slot] = record
                    else:
                        now, limit = v1.NOW + timedelta(seconds=rng.randrange(6)), rng.randrange(4)
                        due = sorted([r for r in expected if r['due_at'] <= now], key=lambda r: r['due_at'])[:limit]
                        self.assertEqual(queue.pop_due(now, limit), due)
                        expected = [r for r in expected if r not in due]
                    self.assertEqual(len(queue), len(expected))
            self.assertEqual(queue.pop_due(v1.NOW + timedelta(days=1)),
                             sorted(expected, key=lambda r: r['due_at']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
