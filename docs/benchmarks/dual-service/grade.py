"""Independent requirement checks. Pass --reference to validate the oracle."""
import csv
import io
import sys
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

if sys.argv[1] == '--reference':
    sys.argv.pop(1)
    from reference import parse_csv, ImportService, retry_delay, RetryQueue, RetryService
else:
    sys.path.insert(0, sys.argv.pop(1))
    from feed.parser import parse_csv
    from feed.service import ImportService
    from retryq.policy import retry_delay
    from retryq.queue import RetryQueue
    from retryq.service import RetryService

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
HEADER = ['tenant', 'transaction_id', 'amount', 'occurred_at']


def document(rows, header=HEADER):
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()


def row(identity='x', tenant='a', amount='1.00', stamp='2026-01-01T00:00:00Z'):
    return [tenant, identity, amount, stamp]


class Store:
    def __init__(self):
        self.calls = []

    def write_many(self, values):
        self.calls.append(values)


class FeedChecks(unittest.TestCase):
    def test_header_normalization_and_bom(self):
        result = parse_csv('\ufeff' + document([row()], [' Tenant ', 'TRANSACTION_ID', 'Amount', 'occurred_at']))
        self.assertEqual(result, [dict(tenant='a', transaction_id='x', amount_cents=100, occurred_at=NOW)])

    def test_invalid_headers(self):
        for header in (HEADER[:-1], HEADER + ['TENANT'], ['a', 'b', 'c', 'd']):
            with self.subTest(header=header), self.assertRaises(ValueError):
                parse_csv(document([row()], header))

    def test_extra_column_and_quote(self):
        result = parse_csv(document([row('x,y') + ['ignored']], HEADER + ['memo']))
        self.assertEqual(result[0]['transaction_id'], 'x,y')
        self.assertEqual(set(result[0]), {'tenant', 'transaction_id', 'amount_cents', 'occurred_at'})

    def test_multiline_quoted_id(self):
        store = Store()
        self.assertEqual(ImportService(store).import_csv(document([row('one\ntwo')])), 1)
        self.assertEqual(store.calls[0][0]['transaction_id'], 'one\ntwo')

    def test_exact_money(self):
        values = [('0.29', 29), ('-0.29', -29), ('1.2300', 123), ('999999999.99', 99999999999)]
        for amount, cents in values:
            with self.subTest(amount=amount):
                result = parse_csv(document([row(amount=amount)]))[0]['amount_cents']
                self.assertIs(type(result), int)
                self.assertEqual(result, cents)

    def test_bad_money(self):
        for amount in ('1.001', 'NaN', 'Infinity', '-Infinity', 'bad', ''):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                parse_csv(document([row(amount=amount)]))

    def test_normalized_time(self):
        record = parse_csv(document([row(stamp='2026-01-01T02:00:00+02:00')]))[0]
        self.assertEqual(record['occurred_at'], NOW)
        self.assertEqual(record['occurred_at'].utcoffset(), timedelta(0))

    def test_bad_or_naive_time(self):
        for stamp in ('2026-01-01T00:00:00', '2026-01-01', 'not-a-date'):
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                parse_csv(document([row(stamp=stamp)]))

    def test_identity_trim_and_case(self):
        results = parse_csv(document([row(' x ', ' a '), row('x', 'A')]))
        self.assertEqual([(v['tenant'], v['transaction_id']) for v in results], [('a', 'x'), ('A', 'x')])

    def test_blank_identity(self):
        for values in (row('  '), row(tenant='')):
            with self.subTest(values=values), self.assertRaises(ValueError):
                parse_csv(document([values]))

    def test_duplicate_normalization_and_order(self):
        values = [row('z'), row('x'), row('z', amount='1.000', stamp='2026-01-01T01:00:00+01:00'), row('z', 'b')]
        results = parse_csv(document(values))
        self.assertEqual([(v['tenant'], v['transaction_id']) for v in results], [('a', 'z'), ('a', 'x'), ('b', 'z')])

    def test_conflicting_duplicate(self):
        with self.assertRaises(ValueError):
            parse_csv(document([row(), row(amount='2')]))

    def test_blank_rows_and_empty_import(self):
        self.assertEqual(len(parse_csv(document([row(), [], [' ', '', '', '']]))), 1)
        for text in ('', '  \n', document([])):
            store = Store()
            self.assertEqual(ImportService(store).import_csv(text), 0)
            self.assertEqual(store.calls, [])

    def test_bad_row_width_is_atomic(self):
        for bad in (row()[:-1], row() + ['extra']):
            store = Store()
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ImportService(store).import_csv(document([row('valid'), bad]))
            self.assertEqual(store.calls, [])

    def test_validation_failure_is_atomic(self):
        for values in ([row('valid'), row('bad', amount='1.001')], [row(), row(amount='2')]):
            store = Store()
            with self.subTest(values=values), self.assertRaises(ValueError):
                ImportService(store).import_csv(document(values))
            self.assertEqual(store.calls, [])

    def test_one_write_for_whole_batch(self):
        store = Store()
        self.assertEqual(ImportService(store).import_csv(document([row('x'), row('y'), row('x')])), 2)
        self.assertEqual(len(store.calls), 1)
        self.assertEqual(len(store.calls[0]), 2)


class RetryChecks(unittest.TestCase):
    def test_exponential_and_cap(self):
        self.assertEqual([retry_delay(n, NOW, base=2, cap=9) for n in range(1, 5)], [2, 4, 8, 9])

    def test_invalid_required_arguments(self):
        for attempt in (0, -1, 1.5, True):
            with self.subTest(attempt=attempt), self.assertRaises(ValueError):
                retry_delay(attempt, NOW)
        for params in ({'base': -1}, {'cap': -1}, {'base': float('inf')}, {'cap': float('nan')}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                retry_delay(1, NOW, **params)
        with self.assertRaises(ValueError):
            retry_delay(1, NOW.replace(tzinfo=None))

    def test_large_attempt_and_zero_limits(self):
        self.assertEqual(retry_delay(100000, NOW), 60)
        self.assertEqual(retry_delay(100000, NOW, base=0), 0)
        self.assertEqual(retry_delay(100000, NOW, cap=0, retry_after='30'), 0)

    def test_numeric_retry_after(self):
        self.assertEqual(retry_delay(3, NOW, retry_after='2'), 4)
        self.assertEqual(retry_delay(1, NOW, retry_after='12.5'), 12.5)
        self.assertEqual(retry_delay(1, NOW, retry_after=900), 60)
        self.assertEqual(retry_delay(1, NOW, retry_after='-3'), 1)

    def test_http_retry_after(self):
        self.assertEqual(retry_delay(1, NOW, retry_after=format_datetime(NOW + timedelta(seconds=30), usegmt=True)), 30)
        self.assertEqual(retry_delay(2, NOW, retry_after=format_datetime(NOW - timedelta(seconds=30), usegmt=True)), 2)

    def test_malformed_retry_after(self):
        for value in ('bad date', 'NaN', 'Infinity', None):
            with self.subTest(value=value):
                self.assertEqual(retry_delay(2, NOW, retry_after=value), 2)

    def test_due_boundary_and_tenant_identity(self):
        queue = RetryQueue()
        queue.enqueue('a', 'x', {}, NOW)
        queue.enqueue('b', 'x', {}, NOW)
        self.assertEqual(len(queue), 2)
        self.assertEqual([x['tenant'] for x in queue.pop_due(NOW)], ['a', 'b'])
        self.assertEqual(len(queue), 0)

    def test_chronological_order_and_limit(self):
        queue = RetryQueue()
        for identity, seconds in [('late', 3), ('early', 1), ('middle', 2)]:
            queue.enqueue('a', identity, {}, NOW + timedelta(seconds=seconds))
        self.assertEqual([x['job_id'] for x in queue.pop_due(NOW + timedelta(seconds=3), 2)], ['early', 'middle'])
        self.assertEqual(len(queue), 1)

    def test_update_and_fifo_ties(self):
        queue = RetryQueue()
        queue.enqueue('a', 'x', {'v': 1}, NOW)
        queue.enqueue('a', 'y', {'v': 2}, NOW)
        queue.enqueue('a', 'x', {'v': 3}, NOW + timedelta(seconds=1))
        self.assertEqual([x['job_id'] for x in queue.pop_due(NOW)], ['y'])
        self.assertEqual(queue.pop_due(NOW + timedelta(seconds=1))[0]['payload'], {'v': 3})
        queue.enqueue('a', 'x', {}, NOW)
        queue.enqueue('a', 'y', {}, NOW)
        queue.enqueue('a', 'x', {'v': 4}, NOW)
        self.assertEqual([x['job_id'] for x in queue.pop_due(NOW)], ['x', 'y'])

    def test_payload_snapshot_and_utc(self):
        queue = RetryQueue()
        payload = {'v': [1]}
        queue.enqueue('a', 'x', payload, NOW.astimezone(timezone(timedelta(hours=2))))
        payload['v'].append(2)
        value = queue.pop_due(NOW)[0]
        self.assertEqual(value['payload'], {'v': [1]})
        self.assertEqual(value['due_at'].utcoffset(), timedelta(0))
        self.assertEqual(set(value), {'tenant', 'job_id', 'payload', 'due_at'})

    def test_invalid_queue_inputs_preserve_state(self):
        queue = RetryQueue()
        queue.enqueue('a', 'x', {}, NOW)
        for limit in (-1, True, 1.2):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                queue.pop_due(NOW, limit)
        self.assertEqual(queue.pop_due(NOW, 0), [])
        with self.assertRaises(ValueError):
            queue.pop_due(NOW.replace(tzinfo=None))
        with self.assertRaises(ValueError):
            queue.enqueue('a', 'x', {'bad': True}, NOW.replace(tzinfo=None))
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue.pop_due(NOW)[0]['payload'], {})

    def test_retryable_statuses(self):
        for status in (408, 429, 500, 503, 599):
            queue = RetryQueue()
            with self.subTest(status=status):
                self.assertIs(RetryService(queue).fail('a', 'x', {}, 1, NOW, status, retry_after='5'), True)
                self.assertEqual(queue.pop_due(NOW + timedelta(seconds=4)), [])
                self.assertEqual(len(queue.pop_due(NOW + timedelta(seconds=5))), 1)

    def test_nonretryable_statuses(self):
        for status in (200, 400, 404, 409, 499, 600):
            queue = RetryQueue()
            queue.enqueue('a', 'old', {}, NOW)
            with self.subTest(status=status):
                self.assertIs(RetryService(queue).fail('a', 'x', {}, 1, NOW, status), False)
                self.assertEqual(len(queue), 1)

    def test_service_validation_does_not_enqueue(self):
        queue = RetryQueue()
        with self.assertRaises(ValueError):
            RetryService(queue).fail('a', 'x', {}, 0, NOW, 503)
        self.assertEqual(len(queue), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
