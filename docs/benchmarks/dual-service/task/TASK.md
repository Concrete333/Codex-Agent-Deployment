# Repair two independent service components

This repository contains a transaction CSV importer and a retry queue. Both
have production-style correctness defects. Repair both, preserve the public
interfaces below, add regression tests and run the tests. They share no code or
mutable state, and their interfaces are settled; neither repair depends on the
other. Use only the Python standard library.

## CSV importer (`feed/`)

`feed.parser.parse_csv(text)` returns a list of normalized records with exactly
`tenant`, `transaction_id`, `amount_cents`, and `occurred_at` keys. `amount_cents`
is an integer and `occurred_at` is a timezone-aware UTC datetime.

- Parse CSV quoting correctly. Accept a UTF-8 BOM and surrounding whitespace or
  case differences in header names. Required columns are `tenant`,
  `transaction_id`, `amount`, `occurred_at`; additional columns are ignored.
  Missing required columns or duplicate normalized header names raise ValueError.
- Trim tenant and transaction IDs; they must be nonempty and remain case-sensitive.
  Ignore blank records. A nonblank row with too few or too many fields is invalid.
- Convert finite decimal amounts exactly to cents, allowing negative values and
  trailing zeroes but rejecting fractions of a cent, NaN and infinity. Do not use
  binary floating point for money. Amounts are within +/- 1,000,000,000 units.
- Parse ISO-8601 timestamps including `Z` and numeric UTC offsets; reject naive
  timestamps and normalize accepted values to UTC.
- Deduplicate on `(tenant, transaction_id)`, preserving first occurrence order.
  Equal normalized records collapse to one; conflicting records with the same
  identity raise ValueError. Different tenants may reuse an ID.
- `feed.service.ImportService(store).import_csv(text)` validates the entire batch
  before any store writes. On valid nonempty input it calls `store.write_many`
  exactly once with the normalized unique records and returns their count.
  On validation failure or empty input it makes no writes. Validation errors
  surface as ValueError, not partial success.

## Retry scheduling (`retryq/`)

`retryq.policy.retry_delay(attempt, now, base=1, cap=60, retry_after=None)` returns
a delay in seconds. `attempt` is a positive integer (not bool); `base` and `cap`
must be finite nonnegative numbers. `now` is a timezone-aware datetime. Invalid
required arguments raise ValueError.

- Local exponential delay is `base * 2**(attempt - 1)`, capped at `cap`. Very large
  attempts must cap without constructing enormous integers or overflowing.
- Retry-After may be a numeric seconds string/number or an HTTP date. Future dates
  are relative to `now`; past dates and negative seconds mean zero. Ignore
  malformed and nonfinite Retry-After values. The final delay is the larger of
  local and server delay, still capped at `cap`. Zero base and zero cap are valid.
- `RetryQueue.enqueue(tenant, job_id, payload, due_at)` schedules by the pair
  `(tenant, job_id)`. Datetimes must be aware and are normalized to UTC. Enqueuing
  an existing pair replaces its payload and due time, retaining its original FIFO
  position for equal due times. Deep-copy payloads on enqueue.
- `RetryQueue.pop_due(now, limit=100)` removes and returns at most `limit` due
  jobs, in due-time order with FIFO ties. Jobs due exactly at `now` are due.
  Returned dicts have `tenant`, `job_id`, `payload`, `due_at` keys. `limit` must be
  a nonnegative integer (not bool); zero is a no-op. Invalid datetimes/limits
  raise ValueError without changing queue state. `len(queue)` is pending count.
- `RetryService(queue).fail(tenant, job_id, payload, attempt, now, status,
  retry_after=None, base=1, cap=60)` schedules and returns True only for HTTP 408,
  429 and 500-599. Other statuses return False without changing the queue. Use the
  delay policy above. Invalid retry parameters must not partially enqueue work.

Change only this task checkout. Do not fetch dependencies, access the network,
inspect benchmark graders or other trials, or start external agent processes
through the shell. Finish with changes, checks and any unresolved issues.
