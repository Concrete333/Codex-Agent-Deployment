"""Contract-derived inputs/expected outputs; independent of parser implementations."""
import csv
import io
import json
import random
from xml.sax.saxutils import escape, quoteattr


def record(ident='a', day='2024-02-29', minor=1234, currency='USD', memo='hello'):
    return {'id': ident, 'date': day, 'amount_minor': minor, 'currency': currency, 'memo': memo}


def csv_text(rows, delimiter=','):
    out = io.StringIO(newline='')
    csv.writer(out, delimiter=delimiter, lineterminator='\r\n').writerows(rows)
    return out.getvalue()


def rendered(fmt, r):
    n = abs(r['amount_minor'])
    amount = f'{n // 100}.{n % 100:02}'
    signed = ('-' if r['amount_minor'] < 0 else '+') + amount
    currency = r['currency'].lower()
    if fmt == 'bank_csv':
        return csv_text([['memo', 'amount', 'date', 'id', 'currency'],
                         [r['memo'], signed, r['date'], r['id'], currency]])
    if fmt == 'euro_csv':
        euro = amount.replace('.', ',')
        day = '/'.join(reversed(r['date'].split('-')))
        return csv_text([['reference', 'booked', 'debit', 'credit', 'ccy', 'description'],
                         [r['id'], day, euro if r['amount_minor'] < 0 else '',
                          '' if r['amount_minor'] < 0 else euro, currency, r['memo']]], ';')
    if fmt == 'events_jsonl':
        return json.dumps({'status': 'posted', 'id': r['id'], 'day': r['date'],
                           'minor': r['amount_minor'], 'currency': currency, 'memo': r['memo']}, ensure_ascii=False) + '\n'
    if fmt == 'statement_xml':
        return (f'<statement currency={quoteattr(currency)}><entry id={quoteattr(r["id"])} '
                f'date={quoteattr(r["date"])} amount={quoteattr(signed)}><memo>{escape(r["memo"])}</memo></entry></statement>')
    if fmt == 'fixed_width':
        return f'{r["id"]:<8}{r["date"].replace("-", "")}{signed[0]}{n:010}{currency}{r["memo"]}\r\n'
    return json.dumps({'currency': currency, 'batches': [{'date': r['date'], 'items': [
        {'id': r['id'], 'direction': 'out' if r['amount_minor'] < 0 else 'in',
         'amount': amount, 'memo': r['memo']}]}]}, ensure_ascii=False)


FORMATS = ('bank_csv', 'euro_csv', 'events_jsonl', 'statement_xml', 'fixed_width', 'batch_json')


def build(hidden=False):
    cases = []
    def add(fmt, name, text, expected=None):
        cases.append({'name': fmt + '/' + name, 'format': fmt, 'text': text,
                      **({'error': True} if expected is None else {'expected': expected})})
    rng = random.Random(7631 if hidden else 195)
    for fmt in FORMATS:
        for i in range(12 if hidden else 6):
            memo = ('café & <tag>; "paid", ' if i % 2 else '  exact spaces  ') + str(i)
            if fmt != 'fixed_width' and i % 3 == 0:
                memo += '\nsecond line'
            r = record(('h' if hidden else 'v') + str(i), '2025-12-31',
                       rng.randrange(-900000, 900000), 'EUR' if i % 2 else 'GBP', memo)
            add(fmt, 'generated-' + str(i), rendered(fmt, r), [r])
        first = record('first', minor=-19, memo=' first ')
        second = record('second', day='2025-01-01', minor=0, memo='second & last')
        one, two = rendered(fmt, first), rendered(fmt, second)
        if fmt in ('bank_csv', 'euro_csv'):
            delimiter = ',' if fmt == 'bank_csv' else ';'
            rows = list(csv.reader(io.StringIO(one), delimiter=delimiter))
            rows += list(csv.reader(io.StringIO(two), delimiter=delimiter))[1:]
            combined = csv_text(rows, delimiter)
        elif fmt in ('events_jsonl', 'fixed_width'):
            combined = one + two
        elif fmt == 'statement_xml':
            entry = two[two.index('<entry'):two.index('</statement>')]
            combined = one.replace('</statement>', entry + '</statement>')
        else:
            obj = json.loads(one)
            obj['batches'] += json.loads(two)['batches']
            combined = json.dumps(obj)
        add(fmt, 'multiple-record-order', combined, [first, second])
        if fmt in ('events_jsonl', 'fixed_width'):
            r = record('unicode', minor=-7, memo='alpha\u2028beta\vomega  ')
            add(fmt, 'unicode-not-line-break', rendered(fmt, r), [r])
    if hidden:
        for fmt in FORMATS:
            r = record('dup', minor=-25, memo='unchanged')
            text = rendered(fmt, r)
            if fmt == 'bank_csv':
                text += csv_text([['again', '-0.25', r['date'], ' dup ', 'usd']])
            elif fmt == 'euro_csv':
                text += csv_text([[' dup ', '29/02/2024', '0,25', '', 'USD', 'again']], ';')
            elif fmt in ('events_jsonl', 'fixed_width'):
                text += rendered(fmt, r)
            elif fmt == 'statement_xml':
                entry = text[text.index('<entry'):text.index('</statement>')]
                text = text.replace('</statement>', entry + '</statement>')
            else:
                obj = json.loads(text)
                obj['batches'].append(obj['batches'][0])
                text = json.dumps(obj)
            add(fmt, 'duplicate-normalized-id', text)
        return cases

    bank_header = ['id', 'date', 'amount', 'currency', 'memo']
    bank_row = ['a', '2024-02-29', '12.34', 'USD', 'hello']
    def bank(row=bank_row, header=bank_header):
        return csv_text([header, row])
    add('bank_csv', 'empty-header-only', csv_text([bank_header]), [])
    add('bank_csv', 'leading-blank-rows', '\r\n' + bank(), [record()])
    add('bank_csv', 'empty-document', '')
    add('bank_csv', 'duplicate-header', bank(header=['id','date','amount','currency','id']))
    add('bank_csv', 'extra-header', bank(bank_row + ['x'], bank_header + ['x']))
    add('bank_csv', 'short-row', bank(bank_row[:-1]))
    add('bank_csv', 'blank-fields-not-blank-row', bank([''] * 5))
    add('bank_csv', 'broken-quote', 'id,date,amount,currency,memo\na,2024-02-29,12.34,USD,"unterminated')
    for amount in ('1.2', '1.234', '1e2', '1,000.00', '--1', '١٢'):
        add('bank_csv', 'bad-amount-' + amount, bank(['a', '2024-02-29', amount, 'USD', '']))
    add('bank_csv', 'strip-id-amount', bank([' a ', '2024-02-29', ' +12.34 ', 'usd', 'hello']), [record()])
    add('bank_csv', 'invalid-date', bank(['a', '2023-02-29', '0', 'USD', '']))
    add('bank_csv', 'date-width', bank(['a', '2024-2-29', '0', 'USD', '']))
    add('bank_csv', 'bad-currency', bank(['a', '2024-02-29', '0', ' US', '']))
    euro_header = ['reference', 'booked', 'debit', 'credit', 'ccy', 'description']
    def euro(debit='', credit='12,34', day='29/02/2024'):
        return csv_text([euro_header, ['a', day, debit, credit, 'EUR', 'memo']], ';')
    add('euro_csv', 'empty-header-only', csv_text([euro_header], ';'), [])
    add('euro_csv', 'debit-zero', euro('0', ''), [record(minor=0, currency='EUR', memo='memo')])
    add('euro_csv', 'both-amounts', euro('1', '2'))
    add('euro_csv', 'neither-amount', euro(' ', ''))
    for value in ('-1,00', '+1', '1.00', '1,2', '1.000,00', '1e2'):
        add('euro_csv', 'bad-money-' + value, euro(value, ''))
    add('euro_csv', 'invalid-date', euro(day='31/04/2024'))
    add('euro_csv', 'date-width', euro(day='1/02/2024'))
    add('euro_csv', 'short-row', csv_text([euro_header, ['a','29/02/2024']], ';'))
    add('euro_csv', 'duplicate-header', csv_text([euro_header[:-1] + ['ccy']], ';'))
    add('euro_csv', 'empty-document', '')
    posted = {'status': 'posted', 'id': 'a', 'day': '2024-02-29', 'minor': 1234, 'currency': 'USD'}
    add('events_jsonl', 'empty', ' \n\r\n', [])
    add('events_jsonl', 'memo-default', json.dumps(posted), [record(memo='')])
    add('events_jsonl', 'pending-invalid-fields-skipped', '{"status":"pending","minor":false}\n' + json.dumps(posted), [record(memo='')])
    for name, text in [('unknown-status','{"status":"deleted"}'), ('missing-status','{}'),
                       ('array','[]'), ('invalid-json','{'), ('duplicate-json-key','{"status":"pending","status":"posted"}'),
                       ('nan-in-pending','{"status":"pending","ignored":NaN}')]:
        add('events_jsonl', name, text)
    for field, bad in [('minor', True), ('minor', 12.0), ('minor', '12'), ('memo', None), ('id', 1)]:
        add('events_jsonl', 'bad-' + field + '-' + repr(bad), json.dumps({**posted, field: bad}))
    add('events_jsonl', 'all-or-error', json.dumps(posted) + '\n{}')
    xml = rendered('statement_xml', record())
    add('statement_xml', 'empty-root', '<statement currency="USD"/>', [])
    for name, text in [('empty',''), ('root','<other currency="USD"/>'),
                       ('root-extra',xml.replace('currency="usd"','currency="usd" x="1"')),
                       ('entry-extra',xml.replace('id="a"','id="a" x="1"')),
                       ('no-memo',xml.replace('<memo>hello</memo>','')),
                       ('two-memo',xml.replace('</entry>','<memo/></entry>')),
                       ('nested-memo',xml.replace('hello','<b/>')),
                       ('memo-attribute',xml.replace('<memo>','<memo x="1">')),
                       ('tail-text',xml.replace('</entry>','</entry>unexpected')),
                       ('entry-text',xml.replace('<memo>','unexpected<memo>')),
                       ('root-text',xml.replace('<entry','unexpected<entry')),
                       ('doctype','<!DOCTYPE statement []>' + xml),
                       ('invalid-empty-currency','<statement currency="US"/>')]:
        add('statement_xml', name, text)
    add('statement_xml', 'empty-memo', xml.replace('<memo>hello</memo>', '<memo/>'), [record(memo='')])
    fixed = rendered('fixed_width', record())
    add('fixed_width', 'empty', '\r\n  \n', [])
    add('fixed_width', 'zero', rendered('fixed_width', record(minor=0)), [record(minor=0)])
    for name, text in [('short',fixed[:29]), ('bad-sign',fixed[:16] + '?' + fixed[17:]),
                       ('bad-digit',fixed[:17] + 'x' + fixed[18:]),
                       ('unicode-digit',fixed[:17] + '١' + fixed[18:]),
                       ('bad-date',fixed[:8] + '20230229' + fixed[16:]),
                       ('blank-id',' ' * 8 + fixed[8:])]:
        add('fixed_width', name, text)
    batch = {'currency': 'USD', 'batches': [{'date': '2024-02-29', 'items': [{'id': 'a', 'direction':'in', 'amount':'12.34'}]}]}
    add('batch_json', 'memo-default', json.dumps(batch), [record(memo='')])
    add('batch_json', 'empty-batches', '{"currency":"usd","batches":[]}', [])
    add('batch_json', 'empty-items', '{"currency":"usd","batches":[{"date":"2024-02-29","items":[]}]}', [])
    for name, text in [('bad-empty-currency','{"currency":"US","batches":[]}'),
                       ('bad-empty-date','{"currency":"USD","batches":[{"date":"2023-02-29","items":[]}]}'),
                       ('duplicate-key','{"currency":"USD","currency":"EUR","batches":[]}'),
                       ('nan','{"currency":"USD","batches":NaN}'), ('array','[]'), ('empty',''),
                       ('extra-root','{"currency":"USD","batches":[],"extra":1}')]:
        add('batch_json', name, text)
    for field, bad in [('direction', 'debit'), ('amount', '-1.00'), ('amount', '+1'), ('amount', 12),
                       ('amount', '1.234'), ('memo', False), ('extra', 1)]:
        obj = json.loads(json.dumps(batch))
        obj['batches'][0]['items'][0][field] = bad
        add('batch_json', 'bad-item-' + field + '-' + repr(bad), json.dumps(obj))
    for fmt in FORMATS:
        add(fmt, 'non-string', None)
    add('unknown', 'format', '')
    add('canonical_json', 'example-regression', json.dumps([record()]), [record()])
    return cases
