"""Stock mutation primitives."""


def reserve_batch(stock, tenant, lines):
    rows = []
    for line in lines:
        key = (tenant, line['sku'])
        quantity = line['quantity']
        available = stock.get(key, 0)
        if quantity > available:
            raise ValueError('insufficient stock')
        stock[key] = available - quantity
        rows.append(dict(sku=line['sku'], quantity=quantity, remaining=stock[key]))
    return rows
