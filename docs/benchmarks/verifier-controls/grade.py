"""Mechanical review grading; final semantic adjudication is mandatory."""
import copy
import json
from pathlib import Path


def grade(review, cases):
    expected = {c['id']: c for c in cases}
    rows = review.get('records', [])
    errors = []
    if review.get('status') != 'complete' or review.get('coverage_gaps') != []:
        errors.append('incomplete status or coverage gaps')
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        return {'complete': False, 'errors': ['invalid records']}
    if [r.get('id') for r in rows] != list(expected):
        errors.append('require every ID once in the supplied order')
    predicted = set()
    for row in rows:
        ident = row.get('id')
        if ident not in expected:
            errors.append('unknown ID')
            continue
        verdict = row.get('verdict')
        findings = row.get('findings')
        if verdict not in ('accept', 'changes_needed') or not isinstance(findings, list):
            errors.append(ident + ': invalid verdict/findings')
            continue
        if bool(findings) != (verdict == 'changes_needed'):
            errors.append(ident + ': verdict contradicts findings')
        if verdict == 'changes_needed':
            predicted.add(ident)
        for f in findings:
            if not isinstance(f, dict) or any(not isinstance(f.get(k), str) or not f[k].strip()
                    for k in ('draft_wording', 'source_quote', 'impact', 'correction')):
                errors.append(ident + ': incomplete finding')
                continue
            if f['source_quote'] not in expected[ident]['source']:
                errors.append(ident + ': source quote is not verbatim')
            if f['draft_wording'] not in expected[ident]['draft']:
                errors.append(ident + ': draft wording is not verbatim')
    positives = {k for k, c in expected.items() if c['error'] is not None}
    return {'complete': not errors, 'errors': errors,
            'provisional_detected_ids': sorted(predicted & positives),
            'provisional_missed_ids': sorted(positives - predicted),
            'provisional_false_alarm_ids': sorted(predicted - positives),
            'semantic_adjudication_required': True}


def qualify(cases):
    assert len(cases) == 12 and len({c['id'] for c in cases}) == 12
    assert sum(c['error'] is not None for c in cases) == 6
    for c in cases:
        assert c['decisive_quote'] in c['source']
    perfect = {'status': 'complete', 'coverage_gaps': [], 'records': []}
    for c in cases:
        f = [] if c['error'] is None else [{'draft_wording': c['draft'],
            'source_quote': c['decisive_quote'], 'impact': c['error']['impact'],
            'correction': c['error']['required_finding']}]
        perfect['records'].append({'id': c['id'], 'verdict': 'changes_needed' if f else 'accept', 'findings': f})
    result = grade(perfect, cases)
    assert result['complete'] and len(result['provisional_detected_ids']) == 6
    empty = copy.deepcopy(perfect)
    for row in empty['records']:
        row.update(verdict='accept', findings=[])
    assert len(grade(empty, cases)['provisional_missed_ids']) == 6
    all_bad = copy.deepcopy(perfect)
    for row, c in zip(all_bad['records'], cases):
        row.update(verdict='changes_needed', findings=[{'draft_wording': c['draft'],
            'source_quote': c['decisive_quote'], 'impact': 'Unsupported allegation', 'correction': 'Unnecessary change'}])
    assert len(grade(all_bad, cases)['provisional_false_alarm_ids']) == 6
    omitted = copy.deepcopy(perfect)
    omitted['records'].pop()
    assert not grade(omitted, cases)['complete']
    invented = copy.deepcopy(perfect)
    invented['records'][1]['findings'][0]['source_quote'] = 'This source does not contain this sentence.'
    assert not grade(invented, cases)['complete']
    wrong_support = copy.deepcopy(perfect)
    wrong_support['records'][1]['findings'][0]['source_quote'] = cases[1]['source'].split('\n')[-1]
    # A verbatim but inadequate quotation cannot be rejected mechanically.
    assert grade(wrong_support, cases)['semantic_adjudication_required']
    literal = all_bad['records'][-1]['findings'][0]['source_quote']
    assert '[io]...' in literal and grade(all_bad, cases)['complete']
    return {'passed': True, 'cases': 12, 'error_cases': 6, 'clean_controls': 6,
            'checks': ['perfect', 'accept-all', 'reject-all', 'omitted-record',
                       'fabricated-quote', 'semantic-check-required', 'literal-punctuation']}


if __name__ == '__main__':
    print(json.dumps(qualify(json.loads(Path(__file__).with_name('cases.json').read_text()))))
