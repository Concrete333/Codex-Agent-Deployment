from .core import reserve_batch


class ReservationService:
    def __init__(self, stock, journal):
        self.stock = stock
        self.journal = journal

    def submit(self, tenant, lines):
        rows = reserve_batch(self.stock, tenant, lines)
        self.journal.append({'tenant': tenant, 'reserved': rows})
        return {'reserved': rows}
