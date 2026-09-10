"""Batch caller which intentionally uses the legacy non-keyed path."""


def ingest_batch(service, tenant, payloads):
    return [service.ingest(tenant, payload) for payload in payloads]
