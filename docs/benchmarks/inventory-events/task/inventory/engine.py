"""Event operations. Complete the component described in SPEC.md."""


def receive(balances, event):
    key = (event['tenant'], event['sku'])
    balances[key] = balances.get(key, 0) + event['quantity']
