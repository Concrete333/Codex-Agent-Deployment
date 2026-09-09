"""Requirement-derived checks; run outside the worker checkout after it exits."""
import sys
import unittest

sys.path.insert(0, sys.argv.pop(1))
from cache import CachedDocuments
from store import DocumentStore


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.store = DocumentStore({('a', 'x'): {'nested': [1]},
                                    ('b', 'x'): {'nested': [2]}})
        self.cache = CachedDocuments(self.store, 10, lambda: self.now)

    def test_tenant_isolation(self):
        self.assertEqual(self.cache.get('a', 'x')['nested'], [1])
        self.assertEqual(self.cache.get('b', 'x')['nested'], [2])

    def test_cache_hit(self):
        self.cache.get('a', 'x')
        self.now = 9.999
        self.cache.get('a', 'x')
        self.assertEqual(self.store.calls, 1)

    def test_exact_expiry(self):
        self.cache.get('a', 'x')
        self.store.documents[('a', 'x')] = {'nested': [3]}
        self.now = 10
        self.assertEqual(self.cache.get('a', 'x')['nested'], [3])
        self.assertEqual(self.store.calls, 2)

    def test_refresh_restarts_ttl(self):
        self.cache.get('a', 'x')
        self.now = 11
        self.cache.get('a', 'x')
        self.now = 20
        self.cache.get('a', 'x')
        self.assertEqual(self.store.calls, 2)

    def test_nonpositive_ttl(self):
        for ttl in (0, -1):
            with self.subTest(ttl=ttl):
                store = DocumentStore({('a', 'x'): {'v': [1]}})
                cache = CachedDocuments(store, ttl, lambda: 0)
                first = cache.get('a', 'x')
                first['v'].append(9)
                self.assertEqual(cache.get('a', 'x'), {'v': [1]})
                self.assertEqual(store.calls, 2)

    def test_mutating_initial_result(self):
        self.cache.get('a', 'x')['nested'].append(8)
        self.assertEqual(self.cache.get('a', 'x')['nested'], [1])
        self.assertEqual(self.store.documents[('a', 'x')]['nested'], [1])

    def test_mutating_cache_hit(self):
        self.cache.get('a', 'x')
        self.cache.get('a', 'x')['nested'].append(8)
        self.assertEqual(self.cache.get('a', 'x')['nested'], [1])

    def test_store_mutation_not_visible_until_expiry(self):
        self.cache.get('a', 'x')
        self.store.documents[('a', 'x')]['nested'].append(8)
        self.assertEqual(self.cache.get('a', 'x')['nested'], [1])
        self.now = 10
        self.assertEqual(self.cache.get('a', 'x')['nested'], [1, 8])

    def test_miss_not_cached(self):
        self.assertIsNone(self.cache.get('a', 'new'))
        self.store.documents[('a', 'new')] = {'v': 3}
        self.assertEqual(self.cache.get('a', 'new'), {'v': 3})

    def test_falsy_document_cached(self):
        self.store.documents[('a', 'empty')] = {}
        self.assertEqual(self.cache.get('a', 'empty'), {})
        self.assertEqual(self.cache.get('a', 'empty'), {})
        self.assertEqual(self.store.calls, 1)

    def test_evict_is_scoped(self):
        self.cache.get('a', 'x')
        self.cache.get('b', 'x')
        self.cache.evict('a', 'x')
        self.cache.evict('missing', 'x')
        self.cache.get('b', 'x')
        self.assertEqual(self.store.calls, 2)
        self.cache.get('a', 'x')
        self.assertEqual(self.store.calls, 3)

    def test_exception_not_cached(self):
        class Flaky:
            calls = 0
            def get(self, tenant, document_id):
                self.calls += 1
                if self.calls == 1:
                    raise RuntimeError('backend unavailable')
                return {'ok': True}
        store = Flaky()
        cache = CachedDocuments(store, 10, lambda: 0)
        with self.assertRaisesRegex(RuntimeError, 'backend unavailable'):
            cache.get('a', 'x')
        self.assertEqual(cache.get('a', 'x'), {'ok': True})
        self.assertEqual(store.calls, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
