import unittest
from cache import CachedDocuments
from store import DocumentStore


class PublicTests(unittest.TestCase):
    def test_read(self):
        store = DocumentStore({('a', 'one'): {'name': 'first'}})
        cache = CachedDocuments(store, 10, lambda: 0)
        self.assertEqual(cache.get('a', 'one'), {'name': 'first'})

    def test_hit_avoids_read(self):
        store = DocumentStore({('a', 'one'): {'name': 'first'}})
        cache = CachedDocuments(store, 10, lambda: 0)
        cache.get('a', 'one')
        cache.get('a', 'one')
        self.assertEqual(store.calls, 1)


if __name__ == '__main__':
    unittest.main()
