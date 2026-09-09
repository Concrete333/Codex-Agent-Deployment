from copy import deepcopy


class CachedDocuments:
    def __init__(self, store, ttl, clock):
        self.store, self.ttl, self.clock = store, ttl, clock
        self.entries = {}

    def get(self, tenant, document_id):
        key = (tenant, document_id)
        now = self.clock()
        if self.ttl > 0 and key in self.entries:
            saved, value = self.entries[key]
            if now - saved < self.ttl:
                return deepcopy(value)
        value = self.store.get(tenant, document_id)
        if self.ttl > 0 and value is not None:
            self.entries[key] = (now, deepcopy(value))
        else:
            self.entries.pop(key, None)
        return deepcopy(value)

    def evict(self, tenant, document_id):
        self.entries.pop((tenant, document_id), None)
