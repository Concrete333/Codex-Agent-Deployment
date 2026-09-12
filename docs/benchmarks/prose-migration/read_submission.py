"""Read a saved answer through the sandbox identity; no inference, writes or ACL changes."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
raw = (root / 'answer.json').read_bytes()
answer = json.loads(raw.decode('utf-8-sig'))
start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
end = int(sys.argv[3]) if len(sys.argv) > 3 else 50
print('ANSWER_SHA256', hashlib.sha256(raw).hexdigest())
for row in answer['records'][start-1:end]:
    print(row['id'], row['disposition'])
    print(row['explanation'])
    for cite in row['evidence']:
        print(f"L{cite['line_start']}-{cite['line_end']}: {cite['quote']}")
    print()
