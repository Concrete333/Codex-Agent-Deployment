from datetime import datetime

REQUIRED = ('tenant', 'transaction_id', 'amount', 'occurred_at')


def normalize(row):
    return {'tenant': row['tenant'], 'transaction_id': row['transaction_id'],
            'amount_cents': int(float(row['amount']) * 100),
            'occurred_at': datetime.fromisoformat(row['occurred_at'])}
