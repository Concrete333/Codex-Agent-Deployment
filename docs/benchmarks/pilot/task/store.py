class DocumentStore:
    def __init__(self, documents):
        self.documents = documents
        self.calls = 0

    def get(self, tenant, document_id):
        self.calls += 1
        return self.documents.get((tenant, document_id))
