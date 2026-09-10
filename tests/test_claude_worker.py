"""Offline checks: never start Claude or consume account usage."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("worker", Path(__file__).parents[1] / "scripts" / "claude_worker.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = dict(id="a", cwd=self.temp.name, model="claude-opus-5", effort="high",
                        profile="review", trusted_context=True, prompt="--tools=default\nUnicode: café")

    def test_missing_config_or_trust_rejected(self):
        for key in ("model", "effort", "profile", "trusted_context", "prompt"):
            job = self.job.copy()
            del job[key]
            with self.assertRaises(ValueError):
                worker.validate({"jobs": [job]})

    def test_xhigh_is_explicit_and_preserved(self):
        job = dict(self.job, effort="xhigh")
        worker.validate({"jobs": [job]})
        self.assertIn("--effort=xhigh", worker.build_args("claude", job))
        with self.assertRaises(ValueError):
            worker.validate({"jobs": [dict(self.job, effort="ultra")]})

    def test_only_opus_5_worker_models_allowed(self):
        for model in ("claude-opus-5", "claude-opus-5-20260908"):
            with self.subTest(model=model):
                worker.validate({"jobs": [dict(self.job, model=model)]})
        for model in ("claude-fable-5-1", "gpt-6-astra", "claude-opus-4-8",
                      "opus", "claude-opus-5-1", "claude-opus-5-arbitrary"):
            with self.subTest(model=model), self.assertRaisesRegex(ValueError, "Only Claude Opus 5"):
                worker.validate({"jobs": [dict(self.job, model=model)]})

    def test_read_only_rejects_shell(self):
        with self.assertRaises(ValueError):
            worker.validate({"jobs": [dict(self.job, allow_shell=True)]})

    def test_tools_and_argument_injection(self):
        args = worker.build_args("claude", dict(self.job, session_id="--tools=default"))
        self.assertNotIn(self.job["prompt"], args)
        self.assertIn("--resume=--tools=default", args)
        self.assertNotIn("Bash", args)
        self.assertNotIn("--fallback-model", args)
        self.assertNotIn("--bare", args)
        self.assertIn("--disable-slash-commands", args)
        self.assertNotIn("--system-prompt", args)
        self.assertEqual(args[args.index("--tools") + 1:args.index("--allowedTools")], ["Read", "Glob", "Grep"])

    def test_edit_shell_is_explicit(self):
        args = worker.build_args("claude", dict(self.job, profile="edit", allow_shell=True))
        self.assertIn("Bash", args)
        self.assertIn("Write", args)

    def test_environment_preserves_windows_and_strips_billing(self):
        with patch.dict(os.environ, {"SystemRoot": "C:/Windows", "USERPROFILE": "C:/Users/example",
                                    "ANTHROPIC_API_KEY": "secret", "ANTHROPIC_BASE_URL": "other",
                                    "CLAUDE_CODE_USE_BEDROCK": "1"}, clear=True):
            env = worker.subscription_env()
        self.assertEqual({k.upper(): v for k, v in env.items()}["SYSTEMROOT"], "C:/Windows")
        self.assertIn("USERPROFILE", env)
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertNotIn("ANTHROPIC_BASE_URL", env)
        self.assertNotIn("CLAUDE_CODE_USE_BEDROCK", env)
        self.assertEqual(env["FORCE_PROMPT_CACHING_5M"], "1")

    def test_cache_override_is_child_only(self):
        with patch.dict(os.environ, {"FORCE_PROMPT_CACHING_5M": "0", "DISABLE_PROMPT_CACHING": "1"}):
            env = worker.subscription_env()
            self.assertEqual(env["FORCE_PROMPT_CACHING_5M"], "1")
            self.assertNotIn("DISABLE_PROMPT_CACHING", env)
            self.assertEqual(os.environ["FORCE_PROMPT_CACHING_5M"], "0")

    def test_cache_version_gate(self):
        for version, valid in (("2.1.104", False), ("2.1.108", True), ("2.1.266", True), ("unknown", False)):
            with patch.object(worker.subprocess, "run", return_value=Mock(returncode=0, stdout=version)):
                if valid:
                    worker.check_cache_support("claude", {})
                else:
                    with self.assertRaises(ValueError):
                        worker.check_cache_support("claude", {})

    def test_compact_receipt_preserves_full_evidence(self):
        receipt = dict(id="a", status="returned", result="é" * 5000, cli_stdout="exact stdout",
                       stderr="exact diagnostic", usage={"input_tokens": 7, "iterations": [{"large": "details"}]})
        compact = worker.compact_receipt(receipt, self.temp.name, 0)
        self.assertEqual(len(compact["result"]), 4000)
        self.assertTrue(compact["result_truncated"])
        self.assertTrue(compact["details_require_read"])
        self.assertNotIn("usage", compact)
        self.assertEqual(json.loads(Path(compact["receipt_path"]).read_text(encoding="utf-8")), receipt)
        with self.assertRaises(FileExistsError):
            worker.compact_receipt(receipt, self.temp.name, 0)

    def test_failure_receipt_requires_full_read(self):
        result = worker.compact_receipt(dict(id="a", status="blocked", error="exact failure"), self.temp.name, 1)
        self.assertTrue(result["details_require_read"])
        self.assertIsNone(result["tokens"]["input_tokens"])

    def test_cache_telemetry(self):
        for creation, expected in (({"ephemeral_5m_input_tokens": 20}, "confirmed_5m"),
                                   ({"ephemeral_1h_input_tokens": 20}, "mismatch"), ({}, "unknown")):
            proc = Mock(returncode=0)
            proc.communicate.return_value = (json.dumps(dict(subtype="success", is_error=False,
                                                           usage={"cache_creation": creation})), "")
            with patch.object(worker.subprocess, "Popen", return_value=proc):
                receipt = worker.run_job("claude", self.job, {})
            self.assertEqual(receipt["cache_ttl_check"], expected)

    def test_parallel_reads_allowed(self):
        jobs, concurrency = worker.validate({"jobs": [self.job, dict(self.job, id="b")], "max_concurrent": 2})
        self.assertEqual(len(jobs), 2)
        self.assertEqual(concurrency, 2)

    def test_parallel_overlap_rejected(self):
        with self.assertRaises(ValueError):
            worker.validate({"jobs": [self.job, dict(self.job, id="b", profile="edit")], "max_concurrent": 2})

    def test_parallel_distinct_checkouts_allowed(self):
        other = Path(self.temp.name) / "other"
        first = Path(self.temp.name) / "first"
        other.mkdir()
        first.mkdir()
        worker.validate({"jobs": [dict(self.job, cwd=str(first), profile="edit"),
                                  dict(self.job, id="b", cwd=str(other), profile="edit")], "max_concurrent": 2})

    def test_duplicate_sessions_rejected(self):
        with self.assertRaises(ValueError):
            worker.validate({"jobs": [dict(self.job, session_id="same"), dict(self.job, id="b", session_id="same")], "max_concurrent": 2})

    def test_invalid_budgets_rejected(self):
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                worker.validate({"jobs": [dict(self.job, max_budget_usd=value)]})

    def test_success_is_not_acceptance(self):
        raw = json.dumps(dict(subtype="success", is_error=False, result="Done", session_id="s", total_cost_usd=0.1))
        result = worker.normalize(self.job, raw, 0)
        self.assertEqual(result["status"], "returned")
        self.assertEqual(result["session_id"], "s")

    def test_denials_errors_and_limits(self):
        for data, expected in [
            (dict(subtype="success", is_error=False, permission_denials=[{"tool_name": "Bash"}]), "blocked"),
            (dict(subtype="error_max_turns", is_error=True), "partial"),
            (dict(subtype="error_max_budget_usd", is_error=True), "partial"),
            (dict(subtype="error_during_execution", is_error=True), "blocked"),
        ]:
            self.assertEqual(worker.normalize(self.job, json.dumps(data), 0)["status"], expected)
        self.assertEqual(worker.normalize(self.job, "garbled", 1)["status"], "blocked")
        self.assertEqual(worker.normalize(self.job, "", None, True)["status"], "partial")

    def test_subscription_auth_only(self):
        for method, passes in (("claude.ai", True), ("api_key", False)):
            result = Mock(returncode=0, stdout=json.dumps(dict(loggedIn=True, authMethod=method, apiProvider="firstParty")))
            with patch.object(worker.subprocess, "run", return_value=result):
                if passes:
                    worker.preflight("claude", self.temp.name, {})
                else:
                    with self.assertRaises(ValueError):
                        worker.preflight("claude", self.temp.name, {})

    def test_prompt_is_stdin(self):
        proc = Mock(returncode=0)
        proc.communicate.return_value = (json.dumps(dict(subtype="success", is_error=False, result="ok")), "")
        with patch.object(worker.subprocess, "Popen", return_value=proc):
            result = worker.run_job("claude", self.job, {})
        proc.communicate.assert_called_once_with(self.job["prompt"], timeout=1800)
        self.assertEqual(result["status"], "returned")

    def test_timeout_requests_tree_cleanup_and_retains_partial(self):
        proc = Mock(returncode=1)
        proc.communicate.side_effect = [subprocess.TimeoutExpired("claude", 1), ("", "stopped")]
        with patch.object(worker.subprocess, "Popen", return_value=proc), patch.object(worker, "stop_tree", return_value=True) as cleanup:
            result = worker.run_job("claude", self.job, {})
        cleanup.assert_called_once_with(proc)
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["termination_succeeded"])
        self.assertTrue(result["ownership_check_required"])

    def test_real_subprocess_roundtrip_without_claude(self):
        program = "import json,sys; print(json.dumps(dict(subtype='success',is_error=False,result=sys.stdin.read(),session_id='mock-session')))"
        with patch.object(worker, "build_args", return_value=[sys.executable, "-X", "utf8", "-c", program]):
            result = worker.run_job(sys.executable, self.job, dict(os.environ))
        self.assertEqual(result["result"], self.job["prompt"])
        self.assertEqual(result["session_id"], "mock-session")
        self.assertEqual(result["status"], "returned")

    def test_real_subprocess_timeout_without_claude(self):
        with patch.object(worker, "build_args", return_value=[sys.executable, "-c", "import time; time.sleep(60)"]):
            result = worker.run_job(sys.executable, dict(self.job, timeout_seconds=1), dict(os.environ))
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["termination_succeeded"])


if __name__ == "__main__":
    unittest.main()
