import unittest
from spans import compact_ranges


class PublicTests(unittest.TestCase):
    def test_disjoint(self):
        self.assertEqual(compact_ranges([(1, 3), (7, 9)]), [(1, 3), (7, 9)])

    def test_overlap(self):
        self.assertEqual(compact_ranges([(1, 5), (3, 8)]), [(1, 8)])


if __name__ == '__main__':
    unittest.main()
