class CachedDocuments:
    def __init__(self, store, ttl, clock):
        self.store = store
        self.ttl = ttl
        self.clock = clock
        self.entries = {}

    def get(self, tenant, document_id):
        now = self.clock()
        if document_id in self.entries:
            saved, value = self.entries[document_id]
            if now - saved <= self.ttl:
                return value
        value = self.store.get(tenant, document_id)
        self.entries[document_id] = (now, value)
        return value

    def evict(self, tenant, document_id):
        self.entries.pop(document_id, None)
