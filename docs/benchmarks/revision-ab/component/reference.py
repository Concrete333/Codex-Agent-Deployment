"""Frozen oracle for the component contract; never copied into measured tasks."""

import copy
import math
import time

from dispatchboard.exceptions import IdempotencyConflict
from dispatchboard.validation import canonical_json, snapshot_json, validate_tenant


def _positive_finite_number(value, label):
    if (type(value) not in (int, float)
            or (type(value) is float and not math.isfinite(value))
            or value <= 0):
        raise ValueError(f"{label} must be a positive finite number")
    return value


def _key(value):
    if type(value) is not str or not 1 <= len(value) <= 128 or value != value.strip():
        raise ValueError("key must be a 1-128 character unpadded string")
    return value


class InMemoryIdempotencyLedger:
    def __init__(self, ttl_seconds, *, clock=time.monotonic):
        self.ttl_seconds = _positive_finite_number(ttl_seconds, "ttl_seconds")
        if not callable(clock):
            raise ValueError("clock must be callable")
        self.clock = clock
        self._entries = {}

    def _now(self):
        value = self.clock()
        if (type(value) not in (int, float)
                or (type(value) is float and not math.isfinite(value))):
            raise ValueError("clock must return a finite number")
        return value

    def execute(self, tenant, key, payload, handler):
        tenant = validate_tenant(tenant)
        key = _key(key)
        fingerprint = canonical_json(payload)
        payload_snapshot = snapshot_json(payload)
        if not callable(handler):
            raise ValueError("handler must be callable")
        now = self._now()
        identity = (tenant, key)
        current = self._entries.get(identity)
        if current is not None and now >= current[0]:
            del self._entries[identity]
            current = None
        if current is not None:
            if current[1] != fingerprint:
                raise IdempotencyConflict(tenant, key)
            return copy.deepcopy(current[2])
        try:
            deadline = now + self.ttl_seconds
        except OverflowError as error:
            raise ValueError("clock plus ttl_seconds must be finite") from error
        if type(deadline) is float and not math.isfinite(deadline):
            raise ValueError("clock plus ttl_seconds must be finite")
        receipt = handler(payload_snapshot)
        stored_receipt = copy.deepcopy(receipt)
        self._entries[identity] = (deadline, fingerprint, stored_receipt)
        return copy.deepcopy(stored_receipt)
