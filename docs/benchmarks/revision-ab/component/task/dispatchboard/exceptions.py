class IdempotencyConflict(ValueError):
    """A tenant reused an unexpired idempotency key for another payload."""

    def __init__(self, tenant, key):
        super().__init__(f"idempotency key conflict for tenant {tenant!r}: {key!r}")
        self.tenant = tenant
        self.key = key
