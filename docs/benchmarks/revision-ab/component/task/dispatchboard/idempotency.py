"""Tenant-scoped in-memory idempotency support."""

import time

from .exceptions import IdempotencyConflict


class InMemoryIdempotencyLedger:
    """Execute successful requests once per tenant/key until their TTL expires."""

    def __init__(self, ttl_seconds, *, clock=time.monotonic):
        self.ttl_seconds = ttl_seconds
        self.clock = clock

    def execute(self, tenant, key, payload, handler):
        raise NotImplementedError("implement the ledger described in TASK.md")
