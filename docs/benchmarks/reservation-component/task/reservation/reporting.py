"""Read-only stock reporting, unrelated to write behavior."""


def available(stock, tenant):
    return {sku: count for (owner, sku), count in stock.items() if owner == tenant}
