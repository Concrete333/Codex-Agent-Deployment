"""Small deliberate counterexamples used only to self-check grader sensitivity."""

import copy
import math

from reference import InMemoryIdempotencyLedger as ReferenceLedger


class AliasedReceiptLedger(ReferenceLedger):
    """Incorrectly exposes one mutable cached receipt on replays."""

    def execute(self, tenant, key, payload, handler):
        result = super().execute(tenant, key, payload, handler)
        identity = (tenant, key)
        if identity in self._entries:
            self._entries[identity] = (
                self._entries[identity][0], self._entries[identity][1], result
            )
            return self._entries[identity][2]
        return result


class SlidingExpiryLedger(ReferenceLedger):
    """Incorrectly refreshes the deadline on each replay."""

    def execute(self, tenant, key, payload, handler):
        identity = (tenant, key)
        existed = identity in self._entries
        result = super().execute(tenant, key, payload, handler)
        if existed and identity in self._entries:
            current = self._entries[identity]
            now = self._now()
            deadline = now + self.ttl_seconds
            if math.isfinite(deadline):
                self._entries[identity] = (deadline, current[1], copy.deepcopy(current[2]))
        return result
