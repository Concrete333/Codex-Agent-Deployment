"""Additional held-out cases; never copied into a participant checkout."""
from boundaries_visible import csv_case, event_case, fixed_case


def cases():
    result = []
    for fmt in ('bank_csv', 'euro_csv'):
        for length in (131072, 131073, 180001):
            memo = ('a;,"\r\nz ' * (length // 8 + 1))[:length]
            assert len(memo) == length
            result.append(csv_case(fmt, memo, 'hidden-size-' + str(length)))
        bad = csv_case(fmt, 'q"\r\n' * 40000, 'hidden-unclosed-long-field')
        assert bad['text'].endswith('"')
        bad['text'] = bad['text'][:-1]
        del bad['expected']
        bad['error'] = True
        result.append(bad)
    return result + [fixed_case('one\rtwo\rtail', 'hidden-cr-sequence'),
                     fixed_case('different\r', 'hidden-cr-final'),
                     event_case(True, '[{"n":-1e999}]', 'hidden-pending-overflow'),
                     event_case(False, '{"nested":[1e999]}', 'hidden-posted-overflow')]
