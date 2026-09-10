# Add tenant-scoped idempotency to event ingestion

`dispatchboard` already ingests JSON-shaped event payloads through
`EventIngestionService`. Implement the in-memory idempotency ledger in
`dispatchboard/idempotency.py` and make only any necessary adjustment to
`dispatchboard/service.py`. Add focused regression tests. Use only the Python
standard library.

## Settled public API

`InMemoryIdempotencyLedger(ttl_seconds, *, clock=time.monotonic)` constructs a
single-threaded, in-memory ledger. `ttl_seconds` must be an `int` or `float` but
not `bool`, finite, and greater than zero. `clock` is an injectable zero-argument
monotonic clock.

`ledger.execute(tenant, key, payload, handler)` returns a receipt:

- `tenant` and `key` are case-sensitive strings, 1 through 128 characters,
  with no leading or trailing whitespace.
- `payload` must be a JSON tree made only from `None`, exact `bool`, exact
  `int`, finite exact `float`, `str`, `list`, and `dict` with string keys.
  Tuples, subclasses, non-string object keys, NaN and infinities are invalid at
  any nesting depth.
- Payload equality is equality of
  `json.dumps(payload, sort_keys=True, separators=(",", ":"),
  ensure_ascii=False, allow_nan=False)`. Thus object insertion order is
  irrelevant, array order is significant, and integer and floating-point JSON
  spellings remain distinct (`1` differs from `1.0`).
- `handler` is called with a deep copy of the validated payload on the first
  attempt. For the same `(tenant, key)` and the same canonical payload before
  expiry, return the stored successful receipt without calling `handler`.
  The same pair with a different payload raises `IdempotencyConflict` without
  calling `handler`. Different tenants are independent.
- A successful entry expires when `clock() >= start + ttl_seconds`, where
  `start` is sampled immediately before the first handler call. Expiry exactly
  at the deadline counts as expired. A replay does not extend the deadline.
  An expired key may be reused with any valid payload.
- If `handler` raises, nothing successful is recorded and a later call may
  retry. The handler's successful return value is the receipt. Snapshot it with
  `copy.deepcopy`; return a separate deep copy on both the original call and
  every replay. Mutating the caller's payload, the object retained by the
  handler, or any returned receipt must not affect later comparisons/results.
- Reject an invalid TTL at construction. Reject invalid tenant, key, payload,
  non-callable handler, or a non-finite/non-numeric clock result before calling
  the handler or mutating ledger state. Public validation errors are
  `ValueError` (with `IdempotencyConflict` remaining its existing subclass).

`EventIngestionService.ingest(tenant, payload, *, idempotency_key=None)` is the
existing service entrypoint. Calls without a key retain the legacy direct path.
Calls with a key use the configured ledger so that the handler and event-store
append occur once for a successful request and the returned `Receipt` follows
the copy semantics above. A keyed call without a configured ledger raises the
existing `RuntimeError`. Handler failure must not append an event and must be
retryable.

## Scope

This is an in-memory, single-process, single-threaded component. Do not add a
database, network service, locks, async behavior, cleanup thread, or dependency.
Do not redesign the surrounding modules.

Modify only `dispatchboard/idempotency.py`, `dispatchboard/service.py` if needed,
and new test files. Existing source modules and `test_public.py` are supplied
context and must remain unchanged. Run the public tests plus your added tests.
Do not inspect benchmark graders, references, or other trial outputs.
