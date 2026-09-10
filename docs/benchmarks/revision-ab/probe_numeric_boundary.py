"""Post-run diagnostic, not part of frozen acceptance: a large valid integer TTL."""
import importlib.util
import json
from pathlib import Path
import sys

target = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(target))
if len(sys.argv) > 2 and sys.argv[2] == '--reference':
    spec = importlib.util.spec_from_file_location('boundary_reference', Path(__file__).parent / 'component/reference.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    Ledger = module.InMemoryIdempotencyLedger
else:
    from dispatchboard.idempotency import InMemoryIdempotencyLedger as Ledger

calls = []


def handler(payload):
    calls.append(payload)
    return {'accepted': True}


ledger = Ledger(10 ** 400, clock=lambda: 100.0)
outcomes = []
for _ in range(2):
    try:
        outcomes.append({'result': ledger.execute('tenant', 'request', {'n': 1}, handler)})
    except Exception as error:
        outcomes.append({'error': type(error).__name__, 'message': str(error)})
print(json.dumps({'ttl': '10**400', 'clock': 100.0, 'outcomes': outcomes,
                  'handler_calls': len(calls), 'replay_ok': len(calls) == 1 and all('result' in o for o in outcomes)}))
