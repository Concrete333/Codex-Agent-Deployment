# Atomic reservations and preview

Implement the following change in the existing `reservation` package. Preserve
the public imports and existing submit-result shape. Python standard library only.

`reserve_batch(stock, tenant, lines, *, dry_run=False)` must:

- Validate tenant and each SKU as a nonempty plain `str`; preserve exact spelling,
  whitespace and case. Whitespace-only strings are valid identities.
- Require `dry_run` to be a plain bool. Each line must be a plain dict with exactly
  `sku` and `quantity`; quantity must be a plain int greater than zero (not bool).
- Accept an iterable of lines, including a single-use generator. Aggregate
  duplicate SKUs and return rows in first-occurrence order. Non-iterable `lines`
  raises ValueError; exceptions from consuming a valid iterator propagate.
- Treat stock as a caller-owned plain dict mapping `(tenant, sku)` to nonnegative
  plain ints. This initial stock invariant can be assumed; unrelated entries
  must not be modified. Missing keys mean zero available and must not be inserted.
- Validate and consume the whole input before changing stock. Insufficient stock
  or invalid inputs raise ValueError, leaving stock unchanged. An exception raised
  by an input iterator propagates unchanged and also leaves stock unchanged.
- On success return fresh rows of exactly `sku`, `quantity` (the aggregate) and
  `remaining` (stock after the proposed reservation). Commit by default; with
  `dry_run=True`, return the identical proposed rows without modifying stock.
  Empty lines return an empty list without modifying stock.
- Never change the caller's line dictionaries. Mutating returned data later
  must not change stock, inputs or already stored journal entries.

`ReservationService.submit(tenant, lines)` must keep its existing result shape
`{"reserved": rows}`. It commits and appends exactly one independent journal
entry `{"tenant": tenant, "reserved": rows}` on every success, including an empty
batch. Reservation/input/availability failures append nothing and leave stock
unchanged. The journal is a caller-owned plain list; assume ordinary list
operations succeed. Custom storage callbacks and allocation failures are out of scope.

Add `ReservationService.preview(tenant, lines)`, returning `{"reserved": rows}`
with no stock or journal changes on success or failure. Preview must use the
same reservation implementation with `dry_run=True`, not a second algorithm.

`reservation.api.handle(service, request)` must preserve its legacy default
commit behavior. It accepts a plain dict with required `tenant` and `lines`,
optional `mode` equal to `"commit"` or `"preview"`, and no other keys. Invalid
request shape or mode raises ValueError with no side effects. Route through the
corresponding service method; return that method's result unchanged. Do not
swallow errors or normalize identifiers. Do not add network or persistence.

You may add focused tests. Run public and your own tests while developing;
the external checker is host-owned and outside your scope. Own the component
and its callers through completion. Report unresolved ambiguities, not invented
requirements. A complete handoff must list all changed source/test files.
