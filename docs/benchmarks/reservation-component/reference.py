"""Qualification implementation; never copy into participant checkouts."""
CORE = '''def reserve_batch(stock, tenant, lines, *, dry_run=False):
    if type(tenant) is not str or not tenant or type(dry_run) is not bool:
        raise ValueError('invalid tenant or dry_run')
    try:
        iterator = iter(lines)
    except TypeError as error:
        raise ValueError('lines must be iterable') from error
    totals = {}
    for line in iterator:
        if type(line) is not dict or set(line) != {'sku', 'quantity'}:
            raise ValueError('invalid line')
        sku, count = line['sku'], line['quantity']
        if type(sku) is not str or not sku or type(count) is not int or count <= 0:
            raise ValueError('invalid sku or quantity')
        totals[sku] = totals.get(sku, 0) + count
    result = []
    for sku, count in totals.items():
        left = stock.get((tenant, sku), 0) - count
        if left < 0:
            raise ValueError('insufficient stock')
        result.append(dict(sku=sku, quantity=count, remaining=left))
    if not dry_run:
        for row in result:
            stock[(tenant, row['sku'])] = row['remaining']
    return result
'''

SERVICE = '''from copy import deepcopy
from .core import reserve_batch

class ReservationService:
    def __init__(self, stock, journal):
        self.stock, self.journal = stock, journal
    def submit(self, tenant, lines):
        rows = reserve_batch(self.stock, tenant, lines)
        self.journal.append(deepcopy({'tenant': tenant, 'reserved': rows}))
        return {'reserved': rows}
    def preview(self, tenant, lines):
        return {'reserved': reserve_batch(self.stock, tenant, lines, dry_run=True)}
'''

API = '''def handle(service, request):
    if (type(request) is not dict or not {'tenant', 'lines'} <= set(request)
            or set(request) - {'tenant', 'lines', 'mode'}):
        raise ValueError('invalid request')
    mode = request.get('mode', 'commit')
    if mode == 'commit':
        return service.submit(request['tenant'], request['lines'])
    if mode == 'preview':
        return service.preview(request['tenant'], request['lines'])
    raise ValueError('invalid mode')
'''
