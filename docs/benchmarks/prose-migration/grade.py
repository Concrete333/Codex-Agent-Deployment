"""Frozen structural/decision checks; explanations also require semantic review.

No model calls or writes. Run: python -B grade.py <candidate checkout>.
Citation-anchor coverage is a diagnostic, not a requirement to use one wording.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def normalize(text):
    return ' '.join(text.split())


def source_text(case):
    return f"# {case['id']}: {case['title']}\n\nQuestion: {case['question']}\n\n{case['text'].strip()}\n"


def grade(root):
    cases = json.loads((HERE / 'cases.json').read_text(encoding='utf-8'))
    errors = []
    for case in cases:
        source = root / 'threads' / (case['id'] + '.md')
        if not source.is_file() or source.read_text(encoding='utf-8') != source_text(case):
            errors.append(case['id'] + ': source missing or changed')
    if (root / 'TASK.md').read_bytes() != (HERE / 'TASK.md').read_bytes():
        errors.append('TASK.md changed')
    answer = json.loads((root / 'answer.json').read_text(encoding='utf-8-sig'))
    if set(answer) != {'release', 'assessed_at', 'records'}:
        errors.append('top-level schema')
    if answer.get('release') != '4.0' or answer.get('assessed_at') != '2031-06-30':
        errors.append('release/date')
    records = answer.get('records', [])
    expected_ids = [case['id'] for case in cases]
    if [row.get('id') for row in records] != expected_ids:
        errors.append('coverage: require every ID once in sorted order')
    by_id = {row.get('id'): row for row in records}
    decisions, citations, anchored = 0, 0, 0
    for case in cases:
        ident = case['id']
        row = by_id.get(ident)
        if row is None:
            continue
        if set(row) != {'id', 'disposition', 'explanation', 'evidence'}:
            errors.append(ident + ': record schema')
        if row.get('disposition') != case['expected_disposition']:
            errors.append(f"{ident}: disposition {row.get('disposition')!r}, expected {case['expected_disposition']!r}")
        else:
            decisions += 1
        explanation = row.get('explanation')
        if not isinstance(explanation, str) or not 1 <= len(explanation.split()) <= 80:
            errors.append(ident + ': explanation must contain 1..80 words')
        lines = source_text(case).splitlines()
        evidence = row.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            errors.append(ident + ': missing evidence')
            continue
        good, words, cited = True, 0, []
        for cite in evidence:
            if not isinstance(cite, dict) or set(cite) != {'line_start', 'line_end', 'quote'}:
                good = False
                continue
            start, end, quote = cite['line_start'], cite['line_end'], cite['quote']
            if (type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines)
                    or not isinstance(quote, str) or not 1 <= len(quote.split()) <= 100):
                good = False
                continue
            words += len(quote.split())
            if normalize(quote) not in normalize('\n'.join(lines[start-1:end])):
                good = False
            cited.append(normalize(quote))
        if words > 160:
            good = False
        if good:
            citations += 1
        else:
            errors.append(ident + ': invalid citation or quote budget')
        if all(any(normalize(anchor) in quote for quote in cited) for anchor in case['decisive_evidence']):
            anchored += 1
    return {'records_expected': len(cases), 'decisions_correct': decisions,
            'records_with_valid_citations': citations, 'author_anchors_covered_diagnostic': anchored,
            'automated_pass': not errors, 'errors': errors,
            'semantic_review_required': 'Check all explanations and citation sufficiency against source; exact author anchors are not mandatory.'}


if __name__ == '__main__':
    try:
        result = grade(Path(sys.argv[1]))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
        result = {'automated_pass': False, 'harness_or_schema_error': str(exc)}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['automated_pass'] else 1)
