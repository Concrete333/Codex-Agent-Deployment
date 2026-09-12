"""Private qualification implementation; never placed in participant checkouts."""
ENGINE = '''
FIELDS = {
    'receive': {'sku'}, 'hold': {'sku', 'hold_id'}, 'release': {'hold_id'},
    'ship': {'hold_id'}, 'transfer': {'sku', 'to_tenant'},
}

def text(value):
    if type(value) is not str or not value:
        raise ValueError('identity')

def validate(event):
    if type(event) is not dict:
        raise ValueError('event')
    kind = event.get('kind')
    if type(kind) is not str or kind not in FIELDS:
        raise ValueError('kind')
    if set(event) != FIELDS[kind] | {'kind', 'event_id', 'tenant', 'quantity'}:
        raise ValueError('fields')
    for key in FIELDS[kind] | {'event_id', 'tenant'}:
        text(event[key])
    if type(event['quantity']) is not int or event['quantity'] <= 0:
        raise ValueError('quantity')
    if kind == 'transfer' and event['tenant'] == event['to_tenant']:
        raise ValueError('same tenant')

def step(stock, holds, event):
    tenant, kind, n = event['tenant'], event['kind'], event['quantity']
    if kind in ('release', 'ship'):
        key = (tenant, event['hold_id'])
        if key not in holds or holds[key]['quantity'] < n:
            raise ValueError('hold unavailable')
        row = holds[key]
        if kind == 'ship':
            stock[(tenant, row['sku'])] -= n
        row['quantity'] -= n
        if row['quantity'] == 0:
            del holds[key]
        return
    key = (tenant, event['sku'])
    if kind == 'receive':
        stock[key] = stock.get(key, 0) + n
        return
    held = sum(v['quantity'] for (t, _), v in holds.items() if t == tenant and v['sku'] == event['sku'])
    if stock.get(key, 0) - held < n:
        raise ValueError('stock unavailable')
    if kind == 'hold':
        hkey = (tenant, event['hold_id'])
        if hkey in holds:
            raise ValueError('open hold')
        holds[hkey] = {'sku': event['sku'], 'quantity': n}
    else:
        stock[key] -= n
        dest = (event['to_tenant'], event['sku'])
        stock[dest] = stock.get(dest, 0) + n
'''
LEDGER = '''
from copy import deepcopy
from .engine import text, validate, step
from .projection import project

class Ledger:
    def __init__(self, initial):
        if type(initial) is not dict:
            raise ValueError('initial')
        for key, n in initial.items():
            if type(key) is not tuple or len(key) != 2:
                raise ValueError('key')
            text(key[0]); text(key[1])
            if type(n) is not int or n < 0:
                raise ValueError('stock')
        self.balances = dict(initial)
        self.holds = {}
        self.seen = {}

    def apply(self, events, *, dry_run=False):
        if type(dry_run) is not bool:
            raise ValueError('dry_run')
        try:
            iterator = iter(events)
        except TypeError as exc:
            raise ValueError('events') from exc
        stock, holds, seen = deepcopy((self.balances, self.holds, self.seen))
        result = []
        for event in iterator:
            validate(event)
            identity = event['event_id']
            if identity in seen:
                original, receipt = seen[identity]
                if event != original:
                    raise ValueError('conflict')
                result.append(dict(receipt, replayed=True))
                continue
            step(stock, holds, event)
            receipt = dict(event_id=identity, kind=event['kind'], sequence=len(seen)+1, replayed=False)
            seen[identity] = (dict(event), dict(receipt))
            result.append(receipt)
        if not dry_run:
            self.balances, self.holds, self.seen = stock, holds, seen
        return result

    def preview(self, events):
        return self.apply(events, dry_run=True)

    def snapshot(self):
        return project(self.balances, self.holds, len(self.seen))
'''
API = '''
def handle(ledger, request):
    if type(request) is not dict or 'events' not in request or set(request) - {'events', 'mode'}:
        raise ValueError('request')
    mode = request.get('mode', 'commit')
    if type(mode) is not str or mode not in ('commit', 'preview'):
        raise ValueError('mode')
    if mode == 'preview':
        return ledger.preview(request['events'])
    return ledger.apply(request['events'])
'''
