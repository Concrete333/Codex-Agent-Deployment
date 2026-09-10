from .parser import parse_csv


class ImportService:
    def __init__(self, store):
        self.store = store

    def import_csv(self, text):
        rows = text.splitlines()
        count = 0
        for line in rows[1:]:
            for record in parse_csv(rows[0] + '\n' + line):
                self.store.write_many([record])
                count += 1
        return count
