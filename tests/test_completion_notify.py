import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("notify", Path(__file__).parents[1] / "scripts/completion_notify.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)
THREAD = "01a07282-493e-7311-87b5-b15beeac50cb"

class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.receipt = self.root / "receipt.json"
        self.receipt.write_text('{"status":"failed"}')

    def test_once_including_failure_receipt(self):
        with patch.object(n.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "queued", "")) as run:
            first = n.notify("codex.exe", THREAD, self.receipt)
            second = n.notify("codex.exe", THREAD, self.receipt)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "queued")
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][1:4], ["queue", "--thread", THREAD])
        self.assertIn(str(self.receipt), run.call_args.args[0][-1])

    def test_uncertain_not_retried(self):
        with patch.object(n.subprocess, "run", side_effect=subprocess.TimeoutExpired("codex", 30)) as run:
            self.assertEqual(n.notify("codex", THREAD, self.receipt)["status"], "unknown")
            n.notify("codex", THREAD, self.receipt)
        run.assert_called_once()

    def test_nonzero_preserved(self):
        with patch.object(n.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "unavailable")):
            result = n.notify("codex", THREAD, self.receipt)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stderr"], "unavailable")

    def test_missing_receipt_does_not_send(self):
        self.receipt.unlink()
        with patch.object(n.subprocess, "run") as run:
            self.assertEqual(n.notify("codex", THREAD, self.receipt)["status"], "failed")
        run.assert_not_called()

    def test_crash_claim_prevents_duplicate(self):
        self.receipt.with_name("receipt.notification.json").write_text('{"status":"attempting"}')
        with patch.object(n.subprocess, "run") as run:
            self.assertEqual(n.notify("codex", THREAD, self.receipt)["status"], "attempting")
        run.assert_not_called()

    def test_receipt_saved_before_notification(self):
        request = {"argv": ["fake"], "cwd": str(self.root), "codex": "codex", "thread": THREAD}
        def inspect(binary, thread, receipt):
            self.assertEqual(json.loads(receipt.read_text())["exit_code"], 7)
        with patch.object(n.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)), patch.object(n, "notify", side_effect=inspect):
            n.execute(request, self.root)

    def test_launch_failure_notifies(self):
        request = {"argv": ["fake"], "cwd": str(self.root), "codex": "codex", "thread": THREAD}
        with patch.object(n.subprocess, "run", side_effect=OSError("missing")), patch.object(n, "notify") as notify:
            n.execute(request, self.root)
        notify.assert_called_once()
        self.assertEqual(json.loads((self.root / "process.json").read_text())["status"], "launch_failed")

    def test_invalid_target(self):
        with self.assertRaises(ValueError):
            n.validate_target("codex", "not-a-uuid")

    def test_intervention_message(self):
        self.receipt.write_text('{"termination_unconfirmed":true,"ownership_check_required":true}')
        with patch.object(n.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            n.notify("codex", THREAD, self.receipt)
        self.assertIn("needs intervention", run.call_args.args[0][-1])
        self.assertNotIn("attempt ended", run.call_args.args[0][-1])

    def test_cli_delivery_status(self):
        for status in ("queued", "failed", "unknown", "attempting"):
            with self.subTest(status=status), patch.object(sys, "argv", [
                    "notify", "notify", "--codex", "fake", "--thread", THREAD,
                    "--receipt", str(self.receipt)]), patch.object(n, "notify", return_value={"status": status}), patch("builtins.print"):
                self.assertEqual(n.main(), 0 if status == "queued" else 1)

    def test_actual_cli_missing_receipt_returns_failure(self):
        self.receipt.unlink()
        result = subprocess.run([sys.executable, "-B", str(Path(n.__file__)), "notify",
                                 "--codex", "missing", "--thread", THREAD,
                                 "--receipt", str(self.receipt)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")

    def test_bom_receipt(self):
        self.receipt.write_text('{"status":"failed"}', encoding="utf-8-sig")
        with patch.object(n.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            self.assertEqual(n.notify("codex", THREAD, self.receipt)["status"], "queued")
        run.assert_called_once()

    def test_invalid_claim_is_unknown_and_preserved(self):
        claim = self.receipt.with_name("receipt.notification.json")
        for content in ("", '{"status":', "[]", "null", "{}", '{"status":"invalid"}'):
            with self.subTest(content=content):
                claim.write_text(content, encoding="utf-8")
                original = claim.read_bytes()
                with patch.object(n.subprocess, "run") as run:
                    self.assertEqual(n.notify("codex", THREAD, self.receipt)["status"], "unknown")
                run.assert_not_called()
                self.assertEqual(claim.read_bytes(), original)

    def test_bom_existing_claim_is_not_retried(self):
        self.receipt.with_name("receipt.notification.json").write_text(
            '{"status":"queued"}', encoding="utf-8-sig")
        with patch.object(n.subprocess, "run") as run:
            self.assertEqual(n.notify("codex", THREAD, self.receipt)["status"], "queued")
        run.assert_not_called()

    def test_request_encodings(self):
        for encoding in ("utf-8", "utf-8-sig"):
            with self.subTest(encoding=encoding):
                request = {"argv": [sys.executable], "cwd": str(self.root),
                           "codex": "fake", "thread": THREAD}
                source = self.root / "input.json"
                source.write_text(json.dumps(request), encoding=encoding)
                folder = self.root / encoding
                with patch.object(sys, "argv", ["notify", "start", "--request",
                        str(source), "--run-dir", str(folder)]), patch.object(
                        n, "validate_target"), patch.object(n.subprocess, "Popen") as launch, patch("builtins.print"):
                    launch.return_value.pid = 123
                    n.main()
                (folder / "request.json").write_text(json.dumps(request), encoding=encoding)
                with patch.object(sys, "argv", ["notify", "_run", "--run-dir", str(folder)]), patch.object(
                        n, "execute", return_value={"status": "queued"}) as execute:
                    self.assertEqual(n.main(), 0)
                execute.assert_called_once_with(request, folder)

    def test_actual_cli_partial_claim_returns_unknown(self):
        claim = self.receipt.with_name("receipt.notification.json")
        claim.write_text('{"status":', encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(Path(n.__file__)), "notify",
                                 "--codex", "missing", "--thread", THREAD,
                                 "--receipt", str(self.receipt)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "unknown")
        self.assertEqual(claim.read_text(), '{"status":')

if __name__ == "__main__":
    unittest.main()
