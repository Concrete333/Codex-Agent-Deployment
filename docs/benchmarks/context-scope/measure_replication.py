"""Audit saved replication traces only; no model calls or worker changes."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re

from analyze import text_blocks
from replicate import POINTER
from experiment import REPO, read, save


def main():
    root = Path(read(POINTER)['root'])
    manifest = read(root / 'manifest.json')
    spec = importlib.util.spec_from_file_location('accounting', REPO / 'docs/benchmarks/revision-ab/summarize.py')
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    rows = []
    for cell in manifest['runs']:
        if not (Path(cell['folder']) / 'result.json').exists():
            continue
        receipt = read(Path(manifest['state']) / read(cell['request'])['id'] / 'receipt.json')
        tid = receipt.get('worker', {}).get('session_id')
        if not tid:
            raise ValueError('Missing worker session identity')
        paths = list((Path.home() / '.codex/sessions').glob(f'*/*/*/rollout-*{tid}*.jsonl'))
        assert len(paths) == 1
        cost = accounting.audit_thread(tid, {'path': paths[0], 'parent': None})
        assert cost['reconciled'] and cost['configurations'] == [('gpt-5.6-luna', 'max')]
        tools, sizes, compactions, truncated, access = Counter(), [], [], [], []
        calls = []
        for line, entry in enumerate(accounting.entries(paths[0]), 1):
            payload = entry.get('payload', {})
            if entry.get('type') == 'compacted':
                compactions.append(line)
            if entry.get('type') != 'response_item':
                continue
            if payload.get('type') in ('function_call', 'custom_tool_call'):
                tools[payload.get('name')] += 1
                calls.append(dict(line=line, name=payload.get('name'), arguments=payload.get('input', payload.get('arguments'))))
            if payload.get('type') in ('function_call_output', 'custom_tool_call_output'):
                texts = text_blocks(payload.get('output', ''))
                sizes.append(sum(len(t) for t in texts))
                if any('Warning: truncated output' in t or re.search(r'\d+ tokens truncated', t) for t in texts):
                    truncated.append(line)
                if any(re.search(r'access.*denied|CreateProcessWithLogonW|cannot find path', t, re.I) for t in texts):
                    access.append(line)
        handoff = read(Path(manifest['state']) / read(cell['request'])['id'] / 'handoff.json')
        row = dict(task=cell['task'], arm=cell['arm'], status=receipt['status'],
            checks=receipt.get('checks'), usd=cost['api_equivalent_usd'], usage=cost['usage'],
            responses=cost['responses'], max_input=cost['max_input'], tool_calls=dict(tools),
            output_chars=sum(sizes), compactions=len(compactions), truncations=truncated,
            access_diagnostic_lines=access, handoff=handoff, native_path=str(paths[0]), call_evidence=calls)
        rows.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ('call_evidence', 'native_path', 'checks')}))
    save(root / 'replication-analysis.json', rows)


if __name__ == '__main__':
    main()
