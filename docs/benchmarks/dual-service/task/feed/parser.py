import csv
import io
from .schema import normalize


def parse_csv(text):
    records = []
    seen = set()
    for row in csv.DictReader(io.StringIO(text)):
        record = normalize(row)
        key = record['transaction_id']
        if key not in seen:
            records.append(record)
            seen.add(key)
    return records
