from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    tenant: str
    payload: Any


@dataclass
class Receipt:
    event_id: str
    accepted: bool = True
    details: dict = field(default_factory=dict)
