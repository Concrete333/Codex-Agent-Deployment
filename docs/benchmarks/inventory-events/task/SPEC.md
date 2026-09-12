# Inventory events

Complete the `inventory` package using Python standard library only. Preserve
the public `Ledger`, `handle` and supplied `project` interfaces. Implement a
single-process, in-memory component; no network, persistence, threads or clocks.

## State and identities

`Ledger(initial)` accepts a plain dict mapping `(tenant, sku)` tuples to
nonnegative plain ints. Each key is a plain two-element tuple of nonempty plain
strings. Reject invalid initial data with ValueError. Copy it; do not retain
caller-owned mutable data. Whitespace and case are meaningful, including
whitespace-only identities. Do not normalize strings. Bool is not a plain int.

The ledger tracks on-hand quantities, open holds, successful new events and
their receipts. A hold key is `(tenant, hold_id)`; its value is a SKU and positive
remaining quantity. Hold IDs can be reused after full release or shipment.
Event IDs are globally unique across tenants, not just unique within a batch.
Only public methods define the interface; internal layout is your choice.

## Event contract

Every event is a plain dict with exactly the keys shown below. All IDs/SKUs/
tenants are nonempty plain strings; quantity is a positive plain int.

| kind | Other required keys | Effect |
|---|---|---|
| receive | event_id, tenant, sku, quantity | Increase on-hand for this exact key; missing starts at zero. |
| hold | event_id, tenant, sku, hold_id, quantity | Create a new hold; reject an already-open hold ID or insufficient available stock. |
| release | event_id, tenant, hold_id, quantity | Release part/all of an existing hold; do not change on-hand. |
| ship | event_id, tenant, hold_id, quantity | Consume part/all of a hold and the same on-hand quantity. |
| transfer | event_id, tenant, to_tenant, sku, quantity | Move available stock to a different exact tenant. Reject same-tenant transfer, even when enough stock exists. |

`kind` itself is a plain string from this table. Available equals on-hand minus
all open holds for that tenant/SKU. A release/ship must not exceed the remaining
hold. Remove exhausted holds. Keep existing zero on-hand keys; never insert
missing keys on failure. Transfer destination starts at zero and is inserted
only on success. Python integers are unbounded. No float conversion.

## Batch, replay and receipts

`Ledger.apply(events, *, dry_run=False)` accepts any iterable, including a
single-use generator. `dry_run` must be a plain bool. Non-iterable events raises
ValueError; errors from consuming a valid iterator propagate unchanged.
Process events in order against staged state: later events see earlier effects.
Any invalid event, unavailable resource, conflicting replay or iterator failure
leaves **all** ledger state unchanged, including holds, receipts and sequence.
Error precedence between multiple invalid inputs is unspecified.

Validate each event's shape/types before lookup. If an event ID already exists
in committed or earlier staged events, an equal event dict (key order irrelevant)
is a replay: do not apply it again or consume a sequence number. A different
event with the same ID raises ValueError, including a different tenant.

Return one fresh receipt per input event, in input order, with exactly:
`{"event_id": id, "kind": kind, "sequence": n, "replayed": bool}`.
Sequence starts at 1 and increments only for successful new events. A replay
uses its original sequence and sets replayed=True; a new event uses False.
Mutating inputs or returned receipts later must not alter ledger state or
future replay detection/receipts. Empty input returns [].

With dry_run=True perform identical validation/staged processing and return the
receipts a commit would produce, but retain no changes or new replay identities.
`Ledger.preview(events)` must call the same batch implementation with
dry_run=True, not implement a second event engine.

## Snapshot and API

`Ledger.snapshot()` returns exactly `{"stock": rows, "holds": rows,
"event_count": n}` using the protected `project` helper. Stock rows include
every stored key, sorted by (tenant, sku), with on_hand, held and available.
Hold rows are sorted by (tenant, hold_id). n counts committed new events, not
input rows or batches. Every snapshot is isolated from later mutations.
You may maintain the helper's expected dictionaries internally or construct
equivalent dictionaries when calling it. Do not reimplement projection.

`handle(ledger, request)` accepts a plain dict with required events, optional
mode, and no other keys. mode defaults to commit; otherwise require a plain
string commit or preview. Reject invalid request shape/mode before invoking
ledger methods. Route to apply or preview and return its result unchanged.

Own `inventory/engine.py`, `inventory/ledger.py`, `inventory/api.py` and optional
`tests/test_worker*.py`. Do not edit other files. The supplied receive helper is
a usable pattern, not a mandated algorithm. No required private symbol names.
Run public/added tests while developing. The host owns independent final checks;
do not read sibling trials, evaluator/reference files, personal context or logs.
Report unresolved ambiguities. Do not delegate or start background processes.
