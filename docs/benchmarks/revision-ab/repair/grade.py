"""Frozen external checks; stdlib only. Target is never edited."""
import copy
import importlib.util
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parent
TARGET = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location('candidate_spans', TARGET / 'spans.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
compact = module.compact_ranges


class Acceptance(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(compact([]), [])

    def test_unsorted_touching(self):
        self.assertEqual(compact([(8, 10), (1, 3), (3, 8)]), [(1, 10)])

    def test_nested(self):
        self.assertEqual(compact([(1, 20), (3, 5), (8, 12), (20, 24)]), [(1, 24)])

    def test_duplicates(self):
        self.assertEqual(compact([(2, 6)] * 5), [(2, 6)])

    def test_zero_width(self):
        self.assertEqual(compact([(0, 0), (5, 5), (1, 3)]), [(1, 3)])

    def test_generator(self):
        self.assertEqual(compact(x for x in [(7, 9), (-4, 7)]), [(-4, 9)])

    def test_input_unchanged(self):
        source = [[9, 20], [1, 3], [3, 9]]
        before = copy.deepcopy(source)
        output = compact(source)
        self.assertEqual(source, before)
        self.assertEqual(output, [(1, 20)])
        self.assertIsNot(output, source)
        self.assertTrue(all(type(pair) is tuple for pair in output))

    def test_large_and_negative(self):
        n = 10 ** 80
        self.assertEqual(compact([(-n, 0), (0, n)]), [(-n, n)])

    def test_invalid_endpoints(self):
        for pair in [(True, 3), (1, False), (1.0, 3), ('1', 3), (None, 3)]:
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                compact([pair])

    def test_invalid_pairs(self):
        for pair in [(), (1,), (1, 2, 3), None, 7, '12', {1, 2}]:
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                compact([pair])

    def test_reversed(self):
        with self.assertRaises(ValueError):
            compact([(5, 3)])

    def test_point_set_oracle(self):
        rng = random.Random(81479)
        for case in range(300):
            source = [tuple(sorted((rng.randrange(-25, 26), rng.randrange(-25, 26))))
                      for _ in range(rng.randrange(20))]
            occupied = sorted({p for lo, hi in source for p in range(lo, hi)})
            expected = []
            for point in occupied:
                if expected and expected[-1][1] == point:
                    expected[-1] = (expected[-1][0], point + 1)
                else:
                    expected.append((point, point + 1))
            with self.subTest(case=case):
                self.assertEqual(compact(copy.deepcopy(source)), expected)

    def test_frozen_existing_files(self):
        if TARGET.name == 'reference':
            return
        for filename in ['TASK.md', 'test_public.py']:
            self.assertEqual((TARGET / filename).read_bytes(), (HERE / 'task' / filename).read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=1)
