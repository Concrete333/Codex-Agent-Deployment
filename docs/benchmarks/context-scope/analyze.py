"""Read saved cells, including interrupted ones. No model calls."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re

from experiment import HERE, POINTER, REPO, read, save


def text_blocks(value):
    if isinstance(value, list):
        return [text for item in value for text in text_blocks(item)]
    if isinstance(value, dict):
        return text_blocks(value.get('output', value.get('text', '')))
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except ValueError:
            return [value]
        if isinstance(decoded, (dict, list)):
            return text_blocks(decoded)
        return [value]
    return []


def main():
    root = Path(read(POINTER)['root'])
    manifest = read(root / 'manifest.json')
    spec = importlib.util.spec_from_file_location('accounting', REPO / 'docs/benchmarks/revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    results = []
    for cell in manifest['runs']:
        if not (Path(cell['folder']) / 'result.json').exists():
            continue
        receipt = read(Path(manifest['state']) / read(cell['request'])['id'] / 'receipt.json')
        tid = receipt.get('worker', {}).get('session_id')
        if not tid:
            continue
        paths = list((Path.home() / '.codex/sessions').glob(f'*/*/*/rollout-*{tid}*.jsonl'))
        if len(paths) != 1:
            raise ValueError(f'Expected one fresh native session for {tid}: {paths}')
        cost = accounting.audit_thread(tid, {'path': paths[0], 'parent': None})
        if not cost.get('reconciled'):
            raise ValueError('Incomplete usage')
        calls, outputs, compactions, truncations = [], [], [], []
        for number, row in enumerate(accounting.entries(paths[0]), 1):
            p = row.get('payload', {})
            if row.get('type') == 'compacted':
                compactions.append(number)
            if row.get('type') != 'response_item':
                continue
            if p.get('type') in ('function_call', 'custom_tool_call'):
                arg = p.get('input', p.get('arguments', ''))
                calls.append({'line': number, 'name': p.get('name'), 'arguments': arg,
                              'call_id': p.get('call_id')})
            if p.get('type') in ('function_call_output', 'custom_tool_call_output'):
                texts = text_blocks(p.get('output', ''))
                outputs.append({'line': number, 'chars': sum(len(t) for t in texts)})
                if any('Warning: truncated output' in t or re.search(r'\d+ tokens truncated', t) for t in texts):
                    truncations.append(number)
        row = {'task': cell['task'], 'arm': cell['arm'], 'status': receipt['status'],
               'comparison_valid': False,
               'comparison_limit': 'Aborted experiment: sandbox cwd failure contaminated retrieval.',
               'offline_grade_available': (Path(cell['folder']) / 'offline-grade.json').exists(),
               'safety_aborted': cell['task'] == 'funding' and cell['arm'] == 'A',
               'api_equivalent_usd': cost['api_equivalent_usd'], 'usage': cost['usage'],
               'responses': cost['responses'], 'max_input': cost['max_input'],
               'configurations': cost['configurations'], 'compactions': len(compactions),
               'truncated_returns': len(truncations), 'captured_tool_output_chars': sum(x['chars'] for x in outputs),
               'tool_calls': dict(Counter(c['name'] for c in calls)), 'native_path': str(paths[0]),
               'call_evidence': calls, 'truncation_lines': truncations}
        if row['safety_aborted']:
            row['usage_limit'] = 'Recorded usage only; interrupted in-flight usage may be missing.'
        results.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ('call_evidence','native_path')}))
    save(root / 'behavior-analysis.json', results)


if __name__ == '__main__':
    main()
