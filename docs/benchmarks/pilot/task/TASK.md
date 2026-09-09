# Repair the document cache

The cache in this small Python repository sometimes returns another tenant's
document, stale data, or data changed by a caller. Repair the implementation
without changing the public method signatures. Add regression tests and run the
available tests. Use only the Python standard library.

Required behavior:

- Documents are identified by `(tenant, document_id)`; cache hits must remain
  isolated by tenant.
- A cached document expires when elapsed time is greater than or equal to `ttl`.
  The injected clock supplies monotonic seconds. A non-positive TTL disables
  caching, so every get reads the store.
- Successful cached reads avoid further store calls before expiry.
- Returned documents and cached snapshots must not share mutable nested data
  with callers or the store. Changing a previous result must not change later
  results. Changing store data directly becomes visible after expiry or eviction.
- Missing documents return `None` and are not cached, so a later insertion is
  visible immediately. Store exceptions propagate and do not become cache hits.
- `evict(tenant, document_id)` removes only that tenant's matching cached entry;
  evicting a missing entry is harmless.

`DocumentStore.calls` counts reads. Preserve these public interfaces and their
observable behavior. Change only files in this task directory. Do not fetch
dependencies, access the network, inspect benchmark graders or other runs, or
start other agent processes through the shell. Finish with a concise account of
changes, checks and unresolved issues.
