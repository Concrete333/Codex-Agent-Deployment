"""Executable reference, never supplied to workers."""
import csv
import io
import math
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime


def aware(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError('Timezone-aware datetime required')
    return value.astimezone(timezone.utc)


def parse_csv(text):
    if not text.strip().lstrip('\ufeff').strip():
        return []
    try:
        reader = csv.reader(io.StringIO(text.lstrip('\ufeff'), newline=''), strict=True)
        header = [h.strip().lower() for h in next(reader)]
        required = {'tenant', 'transaction_id', 'amount', 'occurred_at'}
        if len(set(header)) != len(header) or not required.issubset(header):
            raise ValueError('Invalid columns')
        records = {}
        for fields in reader:
            if not any(v.strip() for v in fields):
                continue
            if len(fields) != len(header):
                raise ValueError('Invalid row width')
            row = dict(zip(header, fields))
            tenant, identity = row['tenant'].strip(), row['transaction_id'].strip()
            if not tenant or not identity:
                raise ValueError('Empty identity')
            amount = Decimal(row['amount'].strip())
            if not amount.is_finite() or amount.copy_abs() > 1_000_000_000:
                raise ValueError('Invalid amount')
            # Shift the exponent without rounding under the ambient Decimal context.
            parts = amount.as_tuple()
            cents = Decimal((parts.sign, parts.digits, parts.exponent + 2))
            if cents != cents.to_integral_value():
                raise ValueError('Fractional cent')
            record = dict(tenant=tenant, transaction_id=identity, amount_cents=int(cents),
                          occurred_at=aware(datetime.fromisoformat(row['occurred_at'].strip())))
            key = tenant, identity
            if key in records and records[key] != record:
                raise ValueError('Conflicting duplicate')
            records[key] = record
        return list(records.values())
    except (csv.Error, InvalidOperation, KeyError, StopIteration) as exc:
        raise ValueError('Invalid CSV') from exc


class ImportService:
    def __init__(self, store):
        self.store = store

    def import_csv(self, text):
        records = parse_csv(text)
        if records:
            self.store.write_many(records)
        return len(records)


def retry_delay(attempt, now, base=1, cap=60, retry_after=None):
    now = aware(now)
    if type(attempt) is not int or attempt < 1:
        raise ValueError('Invalid attempt')
    try:
        if isinstance(base, str) or isinstance(cap, str):
            raise ValueError('Numeric base and cap required')
        base, cap = float(base), float(cap)
        if not all(math.isfinite(x) and x >= 0 for x in (base, cap)):
            raise ValueError('Invalid delay limits')
    except (TypeError, OverflowError) as exc:
        raise ValueError('Invalid delay limits') from exc
    if base == 0 or cap == 0:
        local = 0.0
    else:
        try:
            local = min(cap, math.ldexp(base, attempt - 1))
        except OverflowError:
            local = cap
    server = 0.0
    if retry_after is not None:
        try:
            candidate = float(retry_after)
            if math.isfinite(candidate):
                server = max(0.0, candidate)
        except (TypeError, ValueError, OverflowError):
            try:
                server = max(0.0, (aware(parsedate_to_datetime(retry_after)) - now).total_seconds())
            except (TypeError, ValueError, OverflowError, AttributeError):
                pass
    return min(cap, max(local, server))


class RetryQueue:
    def __init__(self):
        self.jobs = {}

    def enqueue(self, tenant, job_id, payload, due_at):
        value = dict(tenant=tenant, job_id=job_id, payload=deepcopy(payload), due_at=aware(due_at))
        self.jobs[tenant, job_id] = value

    def pop_due(self, now, limit=100):
        now = aware(now)
        if type(limit) is not int or limit < 0:
            raise ValueError('Invalid limit')
        due = sorted((v for v in self.jobs.values() if v['due_at'] <= now), key=lambda v: v['due_at'])[:limit]
        for value in due:
            del self.jobs[value['tenant'], value['job_id']]
        return due

    def __len__(self):
        return len(self.jobs)


class RetryService:
    def __init__(self, queue):
        self.queue = queue

    def fail(self, tenant, job_id, payload, attempt, now, status, retry_after=None, base=1, cap=60):
        if status not in (408, 429) and not 500 <= status <= 599:
            return False
        delay = retry_delay(attempt, now, base, cap, retry_after)
        self.queue.enqueue(tenant, job_id, payload, aware(now) + timedelta(seconds=delay))
        return True
