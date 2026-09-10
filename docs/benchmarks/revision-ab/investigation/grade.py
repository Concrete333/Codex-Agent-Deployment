"""Judge exact findings, traceable citations, coverage and unchanged evidence."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
TARGET = Path(sys.argv.pop(1)).resolve()
FIXTURE = json.loads((HERE.parent / 'local-fixture.json').read_text(encoding='utf-8'))
TRUTH = json.loads(Path(FIXTURE['investigation_truth']).read_text(encoding='utf-8'))
BASE = Path(FIXTURE['investigation_source'])


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.answer = json.loads((TARGET / 'answer.json').read_text(encoding='utf-8'))

    def test_scope_and_date(self):
        self.assertEqual(self.answer['assessed_at'], TRUTH['assessed_at'])
        self.assertEqual(self.answer['services_reviewed'], 120)

    def test_exact_findings(self):
        actual = [{k: row[k] for k in ('service', 'owner', 'reason')} for row in self.answer['findings']]
        expected = [{k: row[k] for k in ('service', 'owner', 'reason')} for row in TRUTH['findings']]
        self.assertEqual(actual, expected)

    def test_citations(self):
        found = {row['service']: row for row in self.answer['findings']}
        for expected in TRUTH['findings']:
            with self.subTest(service=expected['service']):
                refs = found[expected['service']]['evidence']
                for rel, needle in expected['required_evidence'].items():
                    candidates = [item for item in refs if item['path'] == rel]
                    self.assertTrue(candidates, f'Missing evidence {rel}')
                    lines = (TARGET / rel).read_text(encoding='utf-8').splitlines()
                    self.assertTrue(any(type(item['line']) is int and 1 <= item['line'] <= len(lines)
                                        and needle in lines[item['line'] - 1] for item in candidates), rel)
                for item in refs:
                    path = (TARGET / item['path']).resolve()
                    self.assertTrue(path.is_relative_to(TARGET / 'catalogue'))
                    lines = path.read_text(encoding='utf-8').splitlines()
                    self.assertIs(type(item['line']), int)
                    self.assertTrue(1 <= item['line'] <= len(lines))

    def test_catalogue_unchanged(self):
        def hashes(root):
            return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (root / 'catalogue').rglob('*') if p.is_file()}
        self.assertEqual(hashes(TARGET), hashes(BASE))
        self.assertEqual((TARGET / 'TASK.md').read_bytes(), (BASE / 'TASK.md').read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=1)
