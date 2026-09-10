"""Example handler implementations used by local callers."""

from .models import Receipt


class AcknowledgingHandler:
    def __init__(self, prefix="evt"):
        self.prefix = prefix
        self.calls = 0

    def __call__(self, event):
        self.calls += 1
        return Receipt(
            event_id=f"{self.prefix}-{self.calls}",
            details={"tenant": event.tenant, "sequence": self.calls},
        )
