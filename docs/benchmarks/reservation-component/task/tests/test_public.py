import unittest
from reservation import reserve_batch, ReservationService
from reservation.api import handle


class PublicTests(unittest.TestCase):
    def test_commit(self):
        stock = {('a', 'x'): 8}
        self.assertEqual(reserve_batch(stock, 'a', [{'sku': 'x', 'quantity': 3}]),
                         [{'sku': 'x', 'quantity': 3, 'remaining': 5}])
        self.assertEqual(stock, {('a', 'x'): 5})

    def test_aggregate(self):
        self.assertEqual(reserve_batch({('a', 'x'): 8}, 'a',
                         [{'sku': 'x', 'quantity': 2}, {'sku': 'x', 'quantity': 3}]),
                         [{'sku': 'x', 'quantity': 5, 'remaining': 3}])

    def test_atomic_failure(self):
        stock = {('a', 'x'): 8}
        with self.assertRaises(ValueError):
            reserve_batch(stock, 'a', [{'sku': 'x', 'quantity': 2}, {'sku': 'y', 'quantity': 1}])
        self.assertEqual(stock, {('a', 'x'): 8})

    def test_preview_api(self):
        stock, journal = {('a', 'x'): 8}, []
        service = ReservationService(stock, journal)
        self.assertEqual(handle(service, {'tenant': 'a', 'lines': [{'sku': 'x', 'quantity': 3}], 'mode': 'preview'}),
                         {'reserved': [{'sku': 'x', 'quantity': 3, 'remaining': 5}]})
        self.assertEqual((stock, journal), ({('a', 'x'): 8}, []))


if __name__ == '__main__':
    unittest.main()
