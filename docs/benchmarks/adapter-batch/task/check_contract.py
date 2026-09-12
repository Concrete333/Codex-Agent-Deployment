"""Read-only conformance runner. Optional target/cases paths are for external evaluation."""
import json
from pathlib import Path
import sys


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
    cases_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / 'fixtures.json'
    sys.path.insert(0, str(root))
    from imports import parse
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    failures = []
    for case in cases:
        try:
            result = parse(case['format'], case['text'])
            shape = (type(result) is list and all(type(r) is dict and set(r) == {'id','date','amount_minor','currency','memo'}
                     and type(r['amount_minor']) is int and all(type(r[k]) is str for k in ('id','date','currency','memo'))
                     for r in result))
            if case.get('error') or not shape or result != case['expected']:
                failures.append({'case': case['name'], 'expected': 'ValueError' if case.get('error') else case['expected'], 'actual': result})
        except Exception as exc:
            if not (case.get('error') and isinstance(exc, ValueError)):
                failures.append({'case': case['name'], 'exception': type(exc).__name__, 'message': str(exc)})
    print(json.dumps({'cases': len(cases), 'passed': len(cases)-len(failures), 'failures': failures}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
