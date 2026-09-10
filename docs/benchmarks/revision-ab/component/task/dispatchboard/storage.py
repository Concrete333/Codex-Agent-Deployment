"""In-memory storage adapter used by the example service and callers."""

import copy


class MemoryEventStore:
    def __init__(self):
        self._events = []

    def append(self, event):
        self._events.append(copy.deepcopy(event))

    def all_for(self, tenant):
        return [copy.deepcopy(event) for event in self._events if event.tenant == tenant]

    def __len__(self):
        return len(self._events)
