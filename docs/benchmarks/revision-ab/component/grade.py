"""Frozen external requirement checks for the component fixture."""

import argparse
import copy
import hashlib
import io
import json
import math
import sys
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
TASK = FIXTURE / "task"


def _select_target(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=str(TASK))
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--mutant", choices=("alias", "sliding"))
    return parser.parse_args(argv)


ARGS = _select_target(sys.argv[1:])
TARGET = Path(ARGS.target).resolve()
sys.path.insert(0, str(TARGET))
sys.path.insert(0, str(FIXTURE))

from dispatchboard.exceptions import IdempotencyConflict
from dispatchboard.handlers import AcknowledgingHandler
from dispatchboard.models import Receipt
from dispatchboard.service import EventIngestionService
from dispatchboard.storage import MemoryEventStore

if ARGS.reference:
    from reference import InMemoryIdempotencyLedger as Ledger
elif ARGS.mutant == "alias":
    from mutants import AliasedReceiptLedger as Ledger
elif ARGS.mutant == "sliding":
    from mutants import SlidingExpiryLedger as Ledger
else:
    from dispatchboard.idempotency import InMemoryIdempotencyLedger as Ledger


class Clock:
    def __init__(self, value=100.0):
        self.value = value

    def __call__(self):
        return self.value


class LedgerChecks(unittest.TestCase):
    def fresh(self, ttl=10, now=100.0):
        clock = Clock(now)
        return Ledger(ttl, clock=clock), clock

    def counter(self, receipt=None):
        calls = []

        def handler(payload):
            calls.append(copy.deepcopy(payload))
            return receipt if receipt is not None else {"call": len(calls), "nested": []}

        return calls, handler

    def test_identical_request_replays_once(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        first = ledger.execute("alpha", "key", {"a": 1}, handler)
        second = ledger.execute("alpha", "key", {"a": 1}, handler)
        self.assertEqual((first, second), ({"call": 1, "nested": []},) * 2)
        self.assertEqual(len(calls), 1)

    def test_object_order_is_irrelevant(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {"a": 1, "b": [2, 3]}, handler)
        ledger.execute("alpha", "key", {"b": [2, 3], "a": 1}, handler)
        self.assertEqual(len(calls), 1)

    def test_array_order_is_significant(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "key", [1, 2], handler)
        with self.assertRaises(IdempotencyConflict):
            ledger.execute("alpha", "key", [2, 1], handler)
        self.assertEqual(len(calls), 1)

    def test_integer_and_float_spellings_are_distinct(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {"n": 1}, handler)
        with self.assertRaises(IdempotencyConflict):
            ledger.execute("alpha", "key", {"n": 1.0}, handler)
        self.assertEqual(len(calls), 1)

    def test_conflict_preserves_original_success(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {"n": 1}, handler)
        with self.assertRaises(IdempotencyConflict):
            ledger.execute("alpha", "key", {"n": 2}, handler)
        replay = ledger.execute("alpha", "key", {"n": 1}, handler)
        self.assertEqual(replay["call"], 1)
        self.assertEqual(len(calls), 1)

    def test_tenants_are_independent(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "same", {"n": 1}, handler)
        ledger.execute("beta", "same", {"n": 2}, handler)
        self.assertEqual(len(calls), 2)

    def test_handler_receives_payload_copy(self):
        ledger, _ = self.fresh()
        payload = {"values": [1]}

        def handler(received):
            self.assertIsNot(received, payload)
            received["values"].append(2)
            return {"ok": True}

        ledger.execute("alpha", "key", payload, handler)
        self.assertEqual(payload, {"values": [1]})
        ledger.execute("alpha", "key", {"values": [1]}, handler)

    def test_mutating_caller_payload_does_not_change_comparison(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        payload = {"values": [1]}
        ledger.execute("alpha", "key", payload, handler)
        payload["values"].append(2)
        ledger.execute("alpha", "key", {"values": [1]}, handler)
        self.assertEqual(len(calls), 1)

    def test_original_receipt_is_not_exposed(self):
        ledger, _ = self.fresh()
        original = {"nested": [1]}
        calls, handler = self.counter(original)
        returned = ledger.execute("alpha", "key", {}, handler)
        self.assertIsNot(returned, original)
        original["nested"].append(2)
        self.assertEqual(ledger.execute("alpha", "key", {}, handler), {"nested": [1]})

    def test_first_return_mutation_does_not_change_replay(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        first = ledger.execute("alpha", "key", {}, handler)
        first["nested"].append("changed")
        self.assertEqual(ledger.execute("alpha", "key", {}, handler)["nested"], [])

    def test_replay_return_mutation_does_not_change_next_replay(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {}, handler)
        replay = ledger.execute("alpha", "key", {}, handler)
        replay["nested"].append("changed")
        self.assertEqual(ledger.execute("alpha", "key", {}, handler)["nested"], [])

    def test_failure_is_not_recorded(self):
        ledger, _ = self.fresh()
        attempts = []

        def handler(_payload):
            attempts.append(1)
            if len(attempts) == 1:
                raise RuntimeError("temporary")
            return {"ok": True}

        with self.assertRaisesRegex(RuntimeError, "temporary"):
            ledger.execute("alpha", "key", {}, handler)
        self.assertEqual(ledger.execute("alpha", "key", {}, handler), {"ok": True})
        self.assertEqual(len(attempts), 2)

    def test_unexpired_entry_replays(self):
        ledger, clock = self.fresh(ttl=10)
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {}, handler)
        clock.value = 109.999
        ledger.execute("alpha", "key", {}, handler)
        self.assertEqual(len(calls), 1)

    def test_expiry_is_inclusive_at_deadline(self):
        ledger, clock = self.fresh(ttl=10)
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {}, handler)
        clock.value = 110
        self.assertEqual(ledger.execute("alpha", "key", {}, handler)["call"], 2)

    def test_replay_does_not_extend_ttl(self):
        ledger, clock = self.fresh(ttl=10)
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {}, handler)
        clock.value = 109
        ledger.execute("alpha", "key", {}, handler)
        clock.value = 110
        ledger.execute("alpha", "key", {}, handler)
        self.assertEqual(len(calls), 2)

    def test_expired_key_accepts_different_payload(self):
        ledger, clock = self.fresh(ttl=10)
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {"n": 1}, handler)
        clock.value = 110
        ledger.execute("alpha", "key", {"n": 2}, handler)
        self.assertEqual(len(calls), 2)

    def test_invalid_ttl_is_rejected(self):
        for value in (0, -1, True, "10", math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Ledger(value)

    def test_invalid_identity_is_rejected_before_handler(self):
        invalid = ("", " padded", "padded ", "x" * 129, 1, True)
        for field in ("tenant", "key"):
            for value in invalid:
                ledger, _ = self.fresh()
                calls, handler = self.counter()
                args = ["alpha", "key", {}, handler]
                args[0 if field == "tenant" else 1] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    ledger.execute(*args)
                self.assertEqual(calls, [])

    def test_unsupported_json_types_are_rejected_before_handler(self):
        invalid = ((1,), {1: "value"}, {"nested": object()}, {"set": {1}})
        for payload in invalid:
            ledger, _ = self.fresh()
            calls, handler = self.counter()
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                ledger.execute("alpha", "key", payload, handler)
            self.assertEqual(calls, [])

    def test_nonfinite_json_is_rejected_before_handler(self):
        for number in (math.nan, math.inf, -math.inf):
            ledger, _ = self.fresh()
            calls, handler = self.counter()
            with self.subTest(number=number), self.assertRaises(ValueError):
                ledger.execute("alpha", "key", {"nested": [number]}, handler)
            self.assertEqual(calls, [])

    def test_cyclic_json_is_rejected_before_handler(self):
        payload = []
        payload.append(payload)
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        with self.assertRaises(ValueError):
            ledger.execute("alpha", "key", payload, handler)
        self.assertEqual(calls, [])

    def test_noncallable_handler_is_rejected_without_losing_entry(self):
        ledger, _ = self.fresh()
        calls, handler = self.counter()
        ledger.execute("alpha", "key", {}, handler)
        with self.assertRaises(ValueError):
            ledger.execute("alpha", "key", {}, None)
        self.assertEqual(ledger.execute("alpha", "key", {}, handler)["call"], 1)
        self.assertEqual(len(calls), 1)

    def test_bad_clock_is_rejected_before_handler_and_mutation(self):
        clock = Clock(math.nan)
        ledger = Ledger(10, clock=clock)
        calls, handler = self.counter()
        with self.assertRaises(ValueError):
            ledger.execute("alpha", "key", {}, handler)
        self.assertEqual(calls, [])
        clock.value = 1
        ledger.execute("alpha", "key", {}, handler)
        self.assertEqual(len(calls), 1)

    def test_noncallable_clock_is_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            Ledger(10, clock=None)

class ServiceChecks(unittest.TestCase):
    def test_keyed_service_replays_handler_and_store_once(self):
        ledger, _ = LedgerChecks().fresh()
        store = MemoryEventStore()
        handler = AcknowledgingHandler()
        service = EventIngestionService(store, handler, ledger)
        first = service.ingest("alpha", {"kind": "created"}, idempotency_key="k")
        second = service.ingest("alpha", {"kind": "created"}, idempotency_key="k")
        self.assertEqual((first.event_id, second.event_id), ("evt-1", "evt-1"))
        self.assertEqual((handler.calls, len(store)), (1, 1))

    def test_keyed_service_receipts_are_isolated(self):
        ledger, _ = LedgerChecks().fresh()
        store = MemoryEventStore()
        service = EventIngestionService(store, AcknowledgingHandler(), ledger)
        first = service.ingest("alpha", {}, idempotency_key="k")
        first.details["sequence"] = 99
        second = service.ingest("alpha", {}, idempotency_key="k")
        self.assertEqual(second.details["sequence"], 1)

    def test_keyed_handler_failure_is_retryable_and_not_stored(self):
        ledger, _ = LedgerChecks().fresh()
        store = MemoryEventStore()
        attempts = []

        def handler(event):
            attempts.append(event)
            if len(attempts) == 1:
                raise RuntimeError("temporary")
            return Receipt("recovered")

        service = EventIngestionService(store, handler, ledger)
        with self.assertRaises(RuntimeError):
            service.ingest("alpha", {}, idempotency_key="k")
        self.assertEqual(len(store), 0)
        self.assertEqual(service.ingest("alpha", {}, idempotency_key="k").event_id, "recovered")
        self.assertEqual((len(attempts), len(store)), (2, 1))

    def test_unkeyed_legacy_path_remains_non_idempotent(self):
        ledger, _ = LedgerChecks().fresh()
        store = MemoryEventStore()
        handler = AcknowledgingHandler()
        service = EventIngestionService(store, handler, ledger)
        self.assertEqual(service.ingest("alpha", {}).event_id, "evt-1")
        self.assertEqual(service.ingest("alpha", {}).event_id, "evt-2")
        self.assertEqual(len(store), 2)


class IntegrityChecks(unittest.TestCase):
    def test_supplied_nonowned_files_are_unchanged(self):
        if ARGS.reference or ARGS.mutant:
            self.skipTest("oracle sensitivity run")
        expected = json.loads((FIXTURE / "protected_hashes.json").read_text(encoding="utf-8"))
        mismatches = []
        for relative, digest in expected.items():
            path = TARGET / relative
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
            if actual != digest:
                mismatches.append(relative)
        self.assertEqual(mismatches, [], "protected files changed: " + ", ".join(mismatches))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    captured = io.StringIO()
    result = unittest.TextTestRunner(stream=captured, verbosity=0).run(suite)
    print(captured.getvalue(), end="")
    print(
        f"SUMMARY mode={'reference' if ARGS.reference else ARGS.mutant or 'target'} "
        f"run={result.testsRun} failures={len(result.failures)} errors={len(result.errors)} "
        f"skipped={len(result.skipped)}"
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
