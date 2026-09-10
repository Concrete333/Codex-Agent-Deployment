"""Thin HTTP-shaped caller with no networking dependency."""


class WebhookController:
    def __init__(self, service):
        self.service = service

    def post(self, headers, body, tenant):
        key = headers.get("Idempotency-Key")
        receipt = self.service.ingest(tenant, body, idempotency_key=key)
        return {"status": 202, "event_id": receipt.event_id}
