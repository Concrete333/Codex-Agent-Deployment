from .projection import project


class Ledger:
    def __init__(self, initial):
        self.balances = dict(initial)
        self.holds = {}

    def apply(self, events, *, dry_run=False):
        raise NotImplementedError('Implement SPEC.md')

    def preview(self, events):
        raise NotImplementedError('Implement SPEC.md')

    def snapshot(self):
        return project(self.balances, self.holds, 0)
