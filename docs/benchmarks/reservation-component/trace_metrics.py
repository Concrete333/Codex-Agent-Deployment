"""Compact measurements from completed own-session traces only."""
import importlib.util
import json
from pathlib import Path
import re

from experiment import HERE, POINTER, read, save

spec=importlib.util.spec_from_file_location('text_reader',HERE.parent/'context-scope/analyze.py')
reader=importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)


def main():
    root=Path(read(POINTER)['root']); rows=[]
    for item in read(root/'accounting.json')['runs']:
        record=item['accounting']
        if not record.get('reconciled'): continue
        sizes=[]; truncations=[]; diagnostics=[]; compactions=0
        for line,text in enumerate(Path(record['rollout']).read_text(encoding='utf-8').splitlines(),1):
            entry=json.loads(text); payload=entry.get('payload',{})
            compactions+=int(entry.get('type')=='compacted')
            if entry.get('type')!='response_item' or payload.get('type') not in ('function_call_output','custom_tool_call_output'):
                continue
            blocks=reader.text_blocks(payload.get('output',''))
            sizes.append(sum(len(b) for b in blocks))
            if any('Warning: truncated output' in b or re.search(r'\d+ tokens truncated',b) for b in blocks): truncations.append(line)
            if any(re.search(r'access.*denied|CreateProcessWithLogonW|cannot find path|Traceback \(most recent',b,re.I) for b in blocks): diagnostics.append(line)
        row={'arm':item['arm'],'round':item['round'],'status':item['status'],'usd':record['api_equivalent_usd'],
             'responses':record['responses'],'max_input':record['max_input'],'usage':record['usage'],
             'tool_calls':record['tool_calls'],'output_chars':sum(sizes),'compactions':compactions,
             'truncation_lines':truncations,'diagnostic_lines':diagnostics}
        rows.append(row); print(json.dumps(row))
    save(root/'trace-metrics.json',rows)


if __name__=='__main__': main()
