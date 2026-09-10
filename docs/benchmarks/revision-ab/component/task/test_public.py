import unittest

from dispatchboard.batch import ingest_batch
from dispatchboard.handlers import AcknowledgingHandler
from dispatchboard.models import Event, Receipt
from dispatchboard.reporting import event_count_by_tenant
from dispatchboard.serialization import receipt_to_dict
from dispatchboard.service import EventIngestionService
from dispatchboard.storage import MemoryEventStore


class LegacySmokeTests(unittest.TestCase):
    def setUp(self):
        self.store = MemoryEventStore()
        self.handler = AcknowledgingHandler()
        self.service = EventIngestionService(self.store, self.handler)

    def test_direct_ingestion_calls_handler_and_store(self):
        receipt = self.service.ingest("tenant-a", {"kind": "created"})
        self.assertEqual(receipt.event_id, "evt-1")
        self.assertEqual(len(self.store), 1)
        self.assertEqual(self.handler.calls, 1)

    def test_store_snapshots_events(self):
        payload = {"items": [1]}
        self.service.ingest("tenant-a", payload)
        payload["items"].append(2)
        first = self.store.all_for("tenant-a")
        first[0].payload["items"].append(3)
        self.assertEqual(self.store.all_for("tenant-a")[0].payload, {"items": [1]})

    def test_failed_handler_does_not_append(self):
        def fail(_event):
            raise RuntimeError("downstream")

        service = EventIngestionService(self.store, fail)
        with self.assertRaisesRegex(RuntimeError, "downstream"):
            service.ingest("tenant-a", {})
        self.assertEqual(len(self.store), 0)

    def test_batch_and_reporting_callers(self):
        receipts = ingest_batch(self.service, "tenant-a", [{"n": 1}, {"n": 2}])
        self.assertEqual([r.event_id for r in receipts], ["evt-1", "evt-2"])
        self.assertEqual(event_count_by_tenant(self.store, ["tenant-a", "other"]),
                         {"tenant-a": 2, "other": 0})

    def test_receipt_serialization(self):
        value = receipt_to_dict(Receipt("x", details={"source": "test"}))
        self.assertEqual(value, {
            "event_id": "x", "accepted": True, "details": {"source": "test"}
        })

    def test_key_without_ledger_is_rejected(self):
        with self.assertRaises(RuntimeError):
            self.service.ingest("tenant-a", {}, idempotency_key="request-1")
        self.assertEqual(len(self.store), 0)


if __name__ == "__main__":
    unittest.main()
