import copy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import deployment_host as host
import deployment_runner as runner


class HostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="deployment-host-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.cwd = self.root / "checkout"
        self.cwd.mkdir()
        self.state = self.root / "private-state"
        self.bridge = self.cwd / ".bridge"
        (self.cwd / "contract.txt").write_text("fixed contract\n")
        self.job = {"id": "approved-1", "provider": "codex", "model": "gpt-5.6-luna", "effort": "max",
                    "cwd": str(self.cwd), "prompt": "Read contract.txt and return a concise summary.",
                    "profile": "review", "trusted_context": True, "timeout_seconds": 5,
                    "protected_files": ["contract.txt"], "artifacts": [], "checks": []}
        self.ready = None

    def trigger(self, ready, alter=None):
        self.ready = ready
        ticket = runner.read_json(ready["ticket_path"])
        data = host.trigger_data(ticket)
        if alter:
            alter(data)
        host.publish_trigger(Path(ticket["trigger_path"]), data)

    def serve(self, on_ready=None, mock_result=None):
        result = mock_result or {"id": self.job["id"], "status": "ready_for_review", "accepted": False}
        with patch.object(runner, "preflight") as preflight, patch.object(runner, "run", return_value=result) as dispatch:
            receipt = host.serve(self.job, self.state, self.bridge, sys.executable, 1, on_ready or self.trigger)
        return receipt, dispatch, preflight

    def test_only_frozen_host_request_is_dispatched(self):
        original = copy.deepcopy(self.job)
        def ready(packet):
            self.job["prompt"] = "unapproved instruction"
            self.job["model"] = "gpt-6-astra"
            self.trigger(packet)
        result, dispatch, _ = self.serve(ready)
        self.assertEqual(result["status"], "ready_for_review")
        self.assertFalse(result["accepted"])
        dispatch.assert_called_once()
        job = dispatch.call_args.args[0]
        self.assertEqual(job["prompt"], original["prompt"])
        self.assertEqual(job["model"], "gpt-5.6-luna")

    def test_extra_trigger_fields_cannot_supply_host_commands(self):
        result, dispatch, _ = self.serve(lambda packet: self.trigger(packet, lambda data: data.update(argv=["unapproved.exe"])))
        self.assertEqual(result["status"], "blocked")
        self.assertIn("altered trigger", result["error"])
        dispatch.assert_not_called()

    def test_wrong_token_is_rejected(self):
        result, dispatch, _ = self.serve(lambda packet: self.trigger(packet, lambda data: data.update(token="bad")))
        self.assertEqual(result["status"], "blocked")
        dispatch.assert_not_called()

    def test_changed_contract_after_arming_blocks_dispatch(self):
        def ready(packet):
            (self.cwd / "contract.txt").write_text("weaker contract")
            self.trigger(packet)
        result, dispatch, _ = self.serve(ready)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Protected files changed", result["error"])
        dispatch.assert_not_called()

    def test_missing_trigger_expires_without_dispatch(self):
        result, dispatch, _ = self.serve(lambda packet: setattr(self, "ready", packet))
        self.assertEqual(result["status"], "blocked")
        self.assertIn("No trigger", result["error"])
        dispatch.assert_not_called()

    def test_host_ticket_cannot_be_rearmed(self):
        self.serve()
        with self.assertRaises(FileExistsError):
            self.serve()

    def test_existing_worker_attempt_cannot_be_rearmed(self):
        (self.state / self.job["id"]).mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "existing attempt"):
            self.serve()

    def test_bridge_cannot_live_in_private_state(self):
        self.bridge = self.state / "shared"
        with self.assertRaisesRegex(ValueError, "Private state"):
            self.serve()

    def test_host_scripts_cannot_live_in_worker_checkout(self):
        with patch.object(host, "__file__", str(self.cwd / "deployment_host.py")):
            with self.assertRaisesRegex(ValueError, "host scripts outside"):
                self.serve()

    def test_host_executable_cannot_be_client_writable(self):
        with patch.object(runner, "executable", return_value=str(self.cwd / "codex.exe")):
            with self.assertRaisesRegex(ValueError, "Codex executable must be outside"):
                self.serve()

    def test_no_claude_bridge_without_separate_qualification(self):
        self.job.update(provider="claude", model="claude-opus-5", effort="low")
        with self.assertRaisesRegex(ValueError, "Codex workers only"):
            self.serve()

    def test_authentication_failure_creates_no_ticket(self):
        with patch.object(runner, "preflight", side_effect=ValueError("not logged in")):
            with self.assertRaisesRegex(ValueError, "not logged in"):
                host.serve(self.job, self.state, self.bridge, sys.executable, 1)
        self.assertFalse(self.state.exists())

    def test_client_collects_private_result_without_cli_or_redispatch(self):
        result, _, _ = self.serve()
        ticket_path = self.ready["ticket_path"]
        with patch.object(runner, "preflight") as preflight, patch.object(runner, "run") as dispatch:
            self.assertEqual(host.request(ticket_path, 1), result)
            self.assertEqual(host.request(ticket_path, 1), result)
        preflight.assert_not_called()
        dispatch.assert_not_called()
        ticket = runner.read_json(ticket_path)
        self.assertFalse(runner.within(Path(ticket["result_path"]), self.cwd))

    def test_client_does_not_require_access_to_endpoint_ancestors(self):
        result, _, _ = self.serve()
        original_exists = Path.exists
        def restricted_exists(path, *args, **kwargs):
            if path == self.root:
                raise PermissionError("Ancestor metadata denied to sandbox")
            return original_exists(path, *args, **kwargs)
        with patch.object(Path, "exists", restricted_exists):
            self.assertEqual(host.request(self.ready["ticket_path"], 1), result)

    def test_client_endpoint_check_rejects_overlap(self):
        self.assertFalse(host.disjoint(self.cwd, self.bridge, inspect_ancestors=False))
        self.assertFalse(host.disjoint(self.cwd, self.cwd, inspect_ancestors=False))

    def test_host_still_requires_full_ancestor_validation(self):
        self.state.mkdir()
        self.bridge.mkdir()
        original_exists = Path.exists
        def restricted_exists(path, *args, **kwargs):
            if path == self.root:
                raise PermissionError("Uninspectable host boundary")
            return original_exists(path, *args, **kwargs)
        with patch.object(Path, "exists", restricted_exists):
            with self.assertRaises(PermissionError):
                host.disjoint(self.state, self.bridge)

    def test_real_client_triggers_host_then_waits_for_completion(self):
        clients = []
        results = []
        errors = []
        def ready(packet):
            def client():
                try:
                    results.append(host.request(packet["ticket_path"], 5))
                except Exception as exc:
                    errors.append(exc)
            thread = threading.Thread(target=client)
            clients.append(thread)
            thread.start()
        result, dispatch, _ = self.serve(ready)
        for client in clients:
            client.join(6)
            self.assertFalse(client.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(results, [result])
        dispatch.assert_called_once()

    def test_receipt_identity_mismatch_is_not_accepted(self):
        self.serve()
        ticket = runner.read_json(self.ready["ticket_path"])
        runner.atomic_json(Path(ticket["result_path"]), {"id": "other", "request_sha256": ticket["request_sha256"]})
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            host.request(self.ready["ticket_path"], 1)

    def test_large_trigger_cannot_be_used_as_job_payload(self):
        def ready(packet):
            ticket = runner.read_json(packet["ticket_path"])
            Path(ticket["trigger_path"]).write_text(json.dumps({"prompt": "a" * 9000}))
        result, dispatch, _ = self.serve(ready)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("8 KiB", result["error"])
        dispatch.assert_not_called()

    def test_invalid_publish_byte_blocks_dispatch(self):
        def ready(packet):
            ticket = runner.read_json(packet["ticket_path"])
            with Path(ticket["trigger_path"]).open("r+b") as stream:
                stream.seek(host.SLOT_SIZE)
                stream.write(b"x")
        result, dispatch, _ = self.serve(ready)
        self.assertIn("publish byte", result["error"])
        dispatch.assert_not_called()

    def test_payload_without_publish_byte_does_not_dispatch(self):
        def ready(packet):
            ticket = runner.read_json(packet["ticket_path"])
            with Path(ticket["trigger_path"]).open("r+b") as stream:
                stream.write(json.dumps(host.trigger_data(ticket)).encode())
        result, dispatch, _ = self.serve(ready)
        self.assertIn("No trigger", result["error"])
        dispatch.assert_not_called()

    def test_publishing_preserves_file_identity(self):
        def ready(packet):
            ticket = runner.read_json(packet["ticket_path"])
            path = Path(ticket["trigger_path"])
            identity = path.stat().st_ino
            self.trigger(packet)
            self.assertEqual(path.stat().st_ino, identity)
            host.publish_trigger(path, host.trigger_data(ticket))
        _, dispatch, _ = self.serve(ready)
        dispatch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
