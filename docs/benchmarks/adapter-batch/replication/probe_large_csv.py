"""Post-hoc probe inspired by solo replication's added test; not frozen grading.

Run unchanged against every completed submission in a fresh read-only process.
No submission edits, new model calls, or retroactive frozen-score changes.
"""
import csv
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from imports import parse

memo = 'x"\r\ny' * 30000
cases = [
    ('bank_csv', ',', ['id', 'date', 'amount', 'currency', 'memo'],
     ['a', '2024-02-29', '0', 'USD', memo]),
    ('euro_csv', ';', ['reference', 'booked', 'debit', 'credit', 'ccy', 'description'],
     ['a', '29/02/2024', '', '0', 'USD', memo]),
]
expected = [{'id': 'a', 'date': '2024-02-29', 'amount_minor': 0,
             'currency': 'USD', 'memo': memo}]
results = []
for name, delimiter, header, row in cases:
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=delimiter)
    writer.writerow(header)
    writer.writerow(row)
    try:
        actual = parse(name, stream.getvalue()[:-2])
        results.append({'format': name, 'passed': actual == expected})
    except Exception as error:
        results.append({'format': name, 'passed': False,
                        'exception': type(error).__name__, 'message': str(error)})
print(json.dumps({'post_hoc': True, 'memo_characters': len(memo),
                  'python_csv_default_field_limit': csv.field_size_limit(),
                  'results': results}))
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
