"""Stable projection boundary: balances[(tenant, sku)], holds[(tenant, hold_id)]."""


def project(balances, holds, event_count):
    held = {}
    for (tenant, _), hold in holds.items():
        key = (tenant, hold['sku'])
        held[key] = held.get(key, 0) + hold['quantity']
    stock = [{'tenant': t, 'sku': s, 'on_hand': n, 'held': held.get((t, s), 0),
              'available': n-held.get((t, s), 0)} for (t, s), n in sorted(balances.items())]
    rows = [{'tenant': t, 'hold_id': h, 'sku': v['sku'], 'quantity': v['quantity']}
            for (t, h), v in sorted(holds.items())]
    return {'stock': stock, 'holds': rows, 'event_count': event_count}
