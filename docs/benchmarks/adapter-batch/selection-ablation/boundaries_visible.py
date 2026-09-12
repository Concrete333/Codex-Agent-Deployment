"""Compact generated visible cases; expected results do not call the adapters."""
import csv
import io
import json


def record(memo='', ident='edge', minor=0):
    return {'id': ident, 'date': '2024-02-29', 'amount_minor': minor,
            'currency': 'USD', 'memo': memo}


def csv_case(fmt, memo, name):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=',' if fmt == 'bank_csv' else ';')
    if fmt == 'bank_csv':
        writer.writerow(['id', 'date', 'amount', 'currency', 'memo'])
        writer.writerow(['edge', '2024-02-29', '0', 'usd', memo])
    else:
        writer.writerow(['reference', 'booked', 'debit', 'credit', 'ccy', 'description'])
        writer.writerow(['edge', '29/02/2024', '', '0', 'usd', memo])
    return {'name': fmt + '/' + name, 'format': fmt,
            'text': stream.getvalue()[:-2], 'expected': [record(memo)]}


def fixed_case(memo, name):
    return {'name': 'fixed_width/' + name, 'format': 'fixed_width',
            'text': 'edge    20240229+0000000000usd' + memo,
            'expected': [record(memo)]}


def event_case(pending, ignored, name):
    event = {'status': 'pending' if pending else 'posted', 'id': 'edge',
             'day': '2024-02-29', 'minor': 0, 'currency': 'usd'}
    text = json.dumps(event)[:-1] + ', "ignored":' + ignored + '}'
    return {'name': 'events_jsonl/' + name, 'format': 'events_jsonl',
            'text': text, 'expected': [] if pending else [record()]}


def cases():
    memo = 'x"\r\ny' * 30000
    return [csv_case(fmt, memo, 'large-memo') for fmt in ('bank_csv', 'euro_csv')] + [
        fixed_case('left\rright', 'bare-cr'), fixed_case('trailing\r', 'final-cr'),
        event_case(True, '1e999', 'pending-large-number'),
        event_case(False, '1e999', 'posted-ignored-large-number'),
    ]
