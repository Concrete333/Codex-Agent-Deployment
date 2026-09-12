"""Local oracle tests. Does not launch any model or import application code."""
import json
from pathlib import Path
import tempfile
import unittest

from experiment import expected, grade, hashes, normalized


class InventoryOracleTests(unittest.TestCase):
    def test_literal_calls_and_exclusions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src').mkdir()
            source = ('# opts.get("limit")\n'
                      'message = \'opts.get("limit")\'\n'
                      'defaults = {"limit": 2}\n'
                      'def outer():\n'
                      '    def inner():\n'
                      '        return opts.get(\n'
                      '            "limit", other.get("limit", 3))\n'
                      '    return inner\n'
                      'a = opts[key]; b = opts.get(key); c = opts["limit"]\n'
                      'a = opts.get("limit"); b = opts.get("limit")\n')
            (root / 'src' / 'sample.py').write_text(source, encoding='utf-8')
            rows = expected(root, ['limit'])
            self.assertEqual(len(rows), 4)
            self.assertEqual(sorted(r['line'] for r in rows), [6, 7, 10, 10])
            self.assertEqual(sum(normalized(rows).values()), 4)
            self.assertEqual(len(normalized(rows)), 3)

    def test_whitespace_allowed_but_not_wrong_expression(self):
        base = {'path': 'src/a.py', 'line': 1, 'key': 'limit', 'expression': 'opts.get("limit", 2)'}
        self.assertEqual(normalized([base]), normalized([{**base, 'expression': 'opts.get( "limit",\n 2 )'}]))
        self.assertNotEqual(normalized([base]), normalized([{**base, 'expression': 'other.get("limit", 2)'}]))

    def test_grader_preserves_source_and_counts_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src').mkdir()
            p = root / 'src' / 'sample.py'
            p.write_text('x = o.get("limit"); y = o.get("limit")\n', encoding='utf-8')
            gold = {'rows': expected(root, ['limit']), 'corpus': hashes(root)}
            (root / 'inventory.json').write_text(json.dumps(gold['rows']), encoding='utf-8')
            self.assertTrue(grade(root, gold)['accepted'])
            (root / 'inventory.json').write_text(json.dumps(gold['rows'][:1]), encoding='utf-8')
            self.assertFalse(grade(root, gold)['accepted'])
            (root / 'inventory.json').write_text(json.dumps(gold['rows']), encoding='utf-8')
            p.write_text('x = 0\n', encoding='utf-8')
            self.assertFalse(grade(root, gold)['accepted'])


if __name__ == '__main__':
    unittest.main()
