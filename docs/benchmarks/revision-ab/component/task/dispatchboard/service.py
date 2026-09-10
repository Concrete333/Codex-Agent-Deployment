"""Application service coordinating handlers and event storage."""

from .models import Event
from .validation import snapshot_json, validate_tenant


class EventIngestionService:
    def __init__(self, store, handler, ledger=None):
        self.store = store
        self.handler = handler
        self.ledger = ledger

    def _ingest_once(self, tenant, payload):
        tenant = validate_tenant(tenant)
        event = Event(tenant=tenant, payload=snapshot_json(payload))
        receipt = self.handler(event)
        self.store.append(event)
        return receipt

    def ingest(self, tenant, payload, *, idempotency_key=None):
        if idempotency_key is None:
            return self._ingest_once(tenant, payload)
        if self.ledger is None:
            raise RuntimeError("idempotency_key requires a configured ledger")
        return self.ledger.execute(
            tenant,
            idempotency_key,
            payload,
            lambda safe_payload: self._ingest_once(tenant, safe_payload),
        )
