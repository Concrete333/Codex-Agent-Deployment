import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import deployment_runner as runner
import deployment_hash

FIXTURE = Path(__file__).parent / "fixtures" / "runner_worker.py"


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="deployment-runner-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.cwd = self.root / "checkout"
        self.cwd.mkdir()
        self.state = self.root / "private-state"
        self.job = {"id": "task-1", "provider": "codex", "model": "gpt-5.6-luna", "effort": "max",
                    "cwd": str(self.cwd), "prompt": "Inspect the supplied contract. Preserve $() and `quotes` and é.",
                    "profile": "edit", "trusted_context": True, "timeout_seconds": 10,
                    "artifacts": ["result.txt"], "checks": [self.check()]}

    def check(self, code="assert open('result.txt').read() == 'unchanged contract\\n'", name="contract"):
        return {"id": name, "argv": [sys.executable, "-B", "-c", code], "timeout_seconds": 5}

    def run_fake(self, mode="complete", job=None):
        job = runner.validate(job or self.job)
        with patch.object(runner, "preflight") as preflight, patch.object(
                runner, "build_worker", side_effect=lambda binary, j, folder:
                [sys.executable, "-B", str(FIXTURE), j["provider"], mode, str(folder)]), patch.object(
                runner, "build_check", side_effect=lambda binary, j, check: check["argv"]):
            result = runner.run(job, self.state, sys.executable)
        return result, preflight

    def receipt(self, run_id="task-1"):
        return runner.read_json(self.state / run_id / "receipt.json")

    def claude(self):
        job = copy.deepcopy(self.job)
        job.update(provider="claude", model="claude-opus-5", effort="low")
        return job

    def test_readonly_hash_helper_matches_host_and_rejects_traversal(self):
        path = self.cwd / 'data.bin'
        path.write_bytes(bytes(range(256)) * 5000)
        expected = runner.hash_files({'data.bin': path})
        self.assertEqual(deployment_hash.fingerprint(self.cwd, ['data.bin']), expected)
        with self.assertRaises(ValueError):
            deployment_hash.fingerprint(self.cwd, ['../outside'])

    def test_permission_fallback_uses_sandbox_not_model_or_acl_changes(self):
        expected = {'result.txt': 'a' * 64}
        completed = subprocess.CompletedProcess([], 0, json.dumps(expected), '')
        with patch.object(runner, 'hash_files', side_effect=PermissionError), patch.object(
                runner.subprocess, 'run', return_value=completed) as call:
            self.assertEqual(runner.fingerprints(self.job, 'codex.exe'), expected)
        argv = call.call_args.args[0]
        self.assertIn('sandbox', argv)
        self.assertIn(':read-only', argv)
        self.assertNotIn('exec', argv)
        self.assertNotIn('--model', argv)

    def test_permission_fallback_requires_explicit_codex_binary(self):
        with patch.object(runner, 'hash_files', side_effect=PermissionError), patch.object(
                runner.subprocess, 'run') as call:
            with self.assertRaises(PermissionError):
                runner.fingerprints(self.job)
            with self.assertRaises(PermissionError):
                runner.fingerprints(self.claude(), 'claude.exe')
            call.assert_not_called()

    def test_permission_fallback_covers_path_validation_and_preserves_names(self):
        expected = {'result.txt': 'a' * 64}
        with patch.object(runner, 'artifact_path', side_effect=PermissionError), patch.object(
                runner.subprocess, 'run', return_value=subprocess.CompletedProcess(
                    [], 0, json.dumps(expected), '')) as call:
            self.assertEqual(runner.artifact_hashes(self.job, iter(expected), 'codex.exe'), expected)
        self.assertEqual(json.loads(call.call_args.kwargs['input'])['names'], ['result.txt'])

    def test_invalid_artifact_path_does_not_trigger_permission_fallback(self):
        with patch.object(runner.subprocess, 'run') as call:
            with self.assertRaises(ValueError):
                runner.artifact_hashes(self.job, ['../outside'], 'codex.exe')
            call.assert_not_called()

    def test_permission_fallback_rejects_missing_hashes(self):
        with patch.object(runner, 'hash_files', side_effect=PermissionError), patch.object(
                runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '{}', '')):
            with self.assertRaisesRegex(ValueError, 'Invalid sandbox'):
                runner.fingerprints(self.job, 'codex.exe')

    def test_success_is_review_ready_not_accepted(self):
        result, _ = self.run_fake()
        self.assertEqual(result["status"], "ready_for_review")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["checks"], [{"id": "contract", "status": "passed"}])
        receipt = self.receipt()
        self.assertEqual(receipt["artifact_sha256"], receipt["artifact_sha256_after_checks"])
        self.assertEqual(receipt["worker"]["usage"]["input_tokens"], 100)
        self.assertEqual(receipt["worker"]["effective_effort"], "unknown")
        self.assertFalse((self.state / "active.json").exists())
        self.assertIn("$() and `quotes` and é", (self.state / "task-1" / "fixture-stdin.txt").read_text(encoding="utf-8"))

    def test_failed_check_preserves_output_and_does_not_retry(self):
        self.job["checks"] = [self.check("print('EXACT FAILURE'); raise SystemExit(7)")]
        result, preflight = self.run_fake()
        self.assertEqual(result["status"], "checks_failed")
        self.assertEqual(preflight.call_count, 1)
        check = self.receipt()["checks"][0]
        self.assertEqual(check["exit_code"], 7)
        self.assertIn("EXACT FAILURE", Path(check["stdout_path"]).read_text())

    def test_claimed_missing_artifact_stops_before_checks(self):
        result, _ = self.run_fake("missing_artifact")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["checks"], [])

    def test_claimed_outside_artifact_stops_before_checks(self):
        result, _ = self.run_fake("outside_artifact")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["checks"], [])

    def test_review_gate_accepts_unchanged_ready_evidence(self):
        self.run_fake()
        receipt, handoff = runner.review_gate(runner.validate(self.job), self.state)
        self.assertEqual(handoff["status"], "complete")
        self.assertFalse(receipt["accepted"])

    def test_review_gate_rejects_artifact_changed_after_checks(self):
        self.run_fake()
        (self.cwd / "result.txt").write_text("different")
        with self.assertRaisesRegex(ValueError, "Evidence changed"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_rejects_missing_check(self):
        self.run_fake()
        receipt = self.receipt()
        receipt["checks"] = []
        runner.atomic_json(self.state / self.job["id"] / "receipt.json", receipt)
        with self.assertRaisesRegex(ValueError, "Required checks"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_rejects_partial_and_failed_attempts(self):
        self.run_fake("partial")
        with self.assertRaisesRegex(ValueError, "not ready"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_rejects_failed_check(self):
        self.job["checks"] = [self.check("raise SystemExit(1)")]
        self.run_fake()
        with self.assertRaisesRegex(ValueError, "not ready"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_rejects_changed_request(self):
        self.run_fake()
        self.job["prompt"] += " A new requirement."
        with self.assertRaisesRegex(ValueError, "not ready"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_rejects_changed_handoff_status(self):
        self.run_fake()
        path = self.state / self.job["id"] / "handoff.json"
        handoff = runner.read_json(path)
        handoff["status"] = "partial"
        runner.atomic_json(path, handoff)
        with self.assertRaisesRegex(ValueError, "not complete"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_rejects_changed_protected_contract(self):
        contract = self.cwd / "contract.txt"
        contract.write_text("original")
        self.job["protected_files"] = ["contract.txt"]
        self.run_fake()
        contract.write_text("weakened")
        with self.assertRaisesRegex(ValueError, "Evidence changed"):
            runner.review_gate(runner.validate(self.job), self.state)

    def test_review_gate_works_for_claude_receipts(self):
        job = self.claude()
        self.run_fake(job=job)
        receipt, _ = runner.review_gate(runner.validate(job), self.state)
        self.assertEqual(receipt["status"], "ready_for_review")

    def test_same_request_does_not_spawn_again(self):
        first, _ = self.run_fake()
        second, preflight = self.run_fake()
        self.assertEqual(first, second)
        preflight.assert_not_called()

    def test_changed_request_cannot_reuse_id(self):
        self.run_fake()
        self.job["effort"] = "max"
        self.job["prompt"] += " A different outcome."
        with self.assertRaisesRegex(ValueError, "different"):
            self.run_fake()

    def test_claim_blocks_second_dispatch(self):
        self.state.mkdir()
        runner.atomic_json(self.state / "active.json", {"id": "other"})
        with patch.object(runner, "preflight") as preflight:
            with self.assertRaisesRegex(ValueError, "active or unresolved"):
                runner.run(runner.validate(self.job), self.state, sys.executable)
            preflight.assert_not_called()

    def test_incomplete_attempt_cannot_redispatch(self):
        folder = self.state / self.job["id"]
        folder.mkdir(parents=True)
        runner.atomic_json(folder / "request.json", runner.validate(self.job))
        with self.assertRaisesRegex(ValueError, "interrupted"):
            self.run_fake()

    def test_timeout_saves_partial_logs_and_holds_claim(self):
        self.job["timeout_seconds"] = 1
        result, _ = self.run_fake("timeout")
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["ownership_check_required"])
        self.assertTrue((self.state / "active.json").exists())
        self.assertIn("partial evidence", Path(self.receipt()["worker_process"]["stdout_path"]).read_text())
        self.assertFalse(self.receipt()["checks"])
        self.assertTrue(self.receipt()["worker_process"]["termination_succeeded"])
        self.assertEqual(self.receipt()["worker"]["session_id"], "codex-fixture-session")
        self.assertIsNone(self.receipt()["worker"]["usage"])

    def test_check_timeout_holds_claim_and_skips_remaining_checks(self):
        self.job["checks"] = [self.check("import time; print('check evidence', flush=True); time.sleep(30)"), self.check(name="later")]
        self.job["checks"][0]["timeout_seconds"] = 1
        result, _ = self.run_fake()
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["ownership_check_required"])
        self.assertEqual(len(self.receipt()["checks"]), 1)

    def test_worker_partial_or_blocked_does_not_run_checks(self):
        for mode in ("partial", "blocked"):
            with self.subTest(mode=mode):
                self.job["id"] = mode
                result, _ = self.run_fake(mode)
                self.assertEqual(result["status"], mode)
                self.assertFalse(self.receipt(mode)["checks"])

    def test_bad_codex_results_never_pass(self):
        for mode in ("error", "malformed", "missing_completion", "multiple_turns", "nonzero"):
            with self.subTest(mode=mode):
                self.state = self.root / ("state-" + mode)
                result, _ = self.run_fake(mode)
                self.assertEqual(result["status"], "blocked")
                self.assertFalse(self.receipt()["checks"])
                self.assertTrue(Path(self.receipt()["worker_process"]["stdout_path"]).exists())

    def test_claude_structured_result_and_usage(self):
        result, _ = self.run_fake(job=self.claude())
        self.assertEqual(result["status"], "ready_for_review")
        self.assertEqual(result["estimated_cost_usd"], 0.01)
        self.assertEqual(self.receipt()["worker"]["reported_models"], ["claude-opus-5"])
        self.assertEqual(runner.read_json(result["handoff_path"])["status"], "complete")

    def test_claude_limits_denials_and_malformed_handoffs(self):
        for mode, expected in (("limit", "partial"), ("denied", "blocked"), ("malformed", "blocked"), ("bad_usage", "blocked")):
            with self.subTest(mode=mode):
                self.state = self.root / ("state-" + mode)
                result, _ = self.run_fake(mode, self.claude())
                self.assertEqual(result["status"], expected)
                self.assertFalse(self.receipt()["checks"])

    def test_verbose_result_not_echoed_but_retained(self):
        result, _ = self.run_fake("verbose")
        self.assertLess(len(json.dumps(result)), 1800)
        self.assertGreater(len(Path(result["handoff_path"]).read_text()), 100000)

    def test_artifact_mutation_during_check_blocks(self):
        self.job["checks"] = [self.check("open('result.txt', 'w').write('changed')")]
        result, _ = self.run_fake()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("changed during checks", result["error"])

    def test_missing_artifact_blocks(self):
        self.job["artifacts"] = ["missing.txt"]
        result, _ = self.run_fake()
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(self.receipt()["checks"])

    def test_worker_changed_checker_is_not_run(self):
        (self.cwd / "checker.py").write_text("assert False\n")
        self.job["protected_files"] = ["checker.py"]
        result, _ = self.run_fake("tamper")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Protected evidence/checker changed", result["error"])
        self.assertFalse(self.receipt()["checks"])

    def test_checks_cannot_change_protected_evidence(self):
        (self.cwd / "contract.txt").write_text("original")
        self.job["protected_files"] = ["contract.txt"]
        self.job["checks"] = [self.check("open('contract.txt', 'w').write('weaker')")]
        result, _ = self.run_fake()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("changed during checks", result["error"])

    def test_protected_file_validation(self):
        with self.assertRaisesRegex(ValueError, "must exist"):
            runner.validate(dict(self.job, protected_files=["missing.txt"]))

    def test_preflight_failure_makes_no_worker_call_and_releases_claim(self):
        with patch.object(runner, "preflight", side_effect=ValueError("login required")), patch.object(runner, "execute") as execute:
            result = runner.run(runner.validate(self.job), self.state, sys.executable)
        execute.assert_not_called()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("login required", result["error"])
        self.assertFalse((self.state / "active.json").exists())

    def test_exception_after_launch_preserves_claim(self):
        with patch.object(runner, "parse_worker", side_effect=OSError("disk error")):
            result, _ = self.run_fake()
        self.assertTrue(result["ownership_check_required"])
        self.assertTrue((self.state / "active.json").exists())

    def test_dry_run_has_no_side_effects(self):
        with patch.object(runner, "preflight") as preflight, patch.object(runner, "execute") as execute:
            result = runner.run(runner.validate(self.job), self.state, sys.executable, dry_run=True)
        self.assertEqual(result["status"], "dry_run")
        self.assertFalse(self.state.exists())
        preflight.assert_not_called()
        execute.assert_not_called()

    def test_disallowed_models_and_luna_efforts(self):
        for model, effort in (("gpt-6-astra", "high"), ("gpt-5.6-luna", "high"),
                              ("gpt-5.6-luna", "xhigh"), ("gpt-5.6-sol", "ultra")):
            with self.subTest(model=model, effort=effort):
                self.job.update(model=model, effort=effort)
                with self.assertRaises(ValueError):
                    runner.validate(self.job)
        job = self.claude()
        job["model"] = "claude-fable-5-1"
        with self.assertRaises(ValueError):
            runner.validate(job)

    def test_invalid_contract_fields_rejected(self):
        changes = [{"id": "../x"}, {"provider": "unknown"}, {"timeout_seconds": True},
                   {"trusted_context": False}, {"surprise_retry": True},
                   {"artifacts": ["../private"]}, {"artifacts": [str(self.root / "private")]},
                   {"checks": [{"id": "test", "argv": "echo unsafe", "timeout_seconds": 5}]},
                   {"checks": [self.check(), self.check()]}, {"allow_shell": True}]
        for change in changes:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    runner.validate(dict(self.job, **change))

    def test_state_cannot_overlap_checkout(self):
        with self.assertRaisesRegex(ValueError, "separate"):
            runner.run(runner.validate(self.job), self.cwd / "state", sys.executable, True)

    def test_codex_command_fixes_model_effort_sandbox_and_no_delegation(self):
        args = runner.build_worker("codex", self.job, self.state / "task")
        self.assertEqual(args[args.index("--model") + 1], "gpt-5.6-luna")
        self.assertIn('model_reasoning_effort="max"', args)
        self.assertIn("agents.enabled=false", args)
        self.assertIn("features.multi_agent_v2.enabled=false", args)
        self.assertNotIn(self.job["prompt"], args)
        self.assertEqual(args[-1], "-")
        self.job["profile"] = "review"
        args = runner.build_worker("codex", self.job, self.state / "task")
        self.assertEqual(args[args.index("--sandbox") + 1], "read-only")

    def test_codex_checks_run_in_sandbox_with_same_write_profile(self):
        for profile, expected in (("edit", ":workspace"), ("review", ":read-only")):
            self.job["profile"] = profile
            args = runner.build_check("codex.exe", self.job, self.check())
            self.assertEqual(args[:4], ["codex.exe", "sandbox", "-P", expected])
            self.assertEqual(args[args.index("--") + 1:], self.check()["argv"])

    def test_codex_does_not_inherit_host_secrets_or_interpreter_hooks(self):
        with patch.dict(os.environ, {"UNRELATED_SECRET": "secret", "PYTHONPATH": "untrusted",
                                     "NODE_OPTIONS": "untrusted", "OPENAI_API_KEY": "secret",
                                     "USERPROFILE": "profile", "SystemRoot": "runtime"}, clear=True):
            self.assertEqual({k.upper(): v for k, v in runner.worker_env("codex").items()}, {"USERPROFILE": "profile", "SYSTEMROOT": "runtime"})

    def test_authorized_protected_baseline_cannot_be_reset(self):
        contract = self.cwd / "contract.txt"
        contract.write_text("approved")
        self.job["protected_files"] = ["contract.txt"]
        job = runner.validate(self.job)
        baseline = runner.protected_hashes(job)
        contract.write_text("changed after authorization")
        with patch.object(runner, "preflight") as preflight, patch.object(runner, "execute") as execute:
            result = runner.run(job, self.state, sys.executable, expected_protected=baseline)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("authorized baseline", result["error"])
        preflight.assert_not_called()
        execute.assert_not_called()

    def test_claude_command_preserves_wrapper_controls(self):
        args = runner.build_worker("claude", self.claude(), self.state / "task")
        self.assertIn("--json-schema", args)
        self.assertIn("--disable-slash-commands", args)
        self.assertIn("--model=claude-opus-5", args)
        self.assertIn("--effort=low", args)
        self.assertEqual(args[args.index("--permission-mode") + 1], "dontAsk")

    def test_release_requires_confirmation_and_dead_recorded_processes(self):
        self.state.mkdir()
        (self.state / "task-1").mkdir()
        claim = {"id": "task-1", "runner_pid": 123, "process_pids": [456]}
        runner.atomic_json(self.state / "active.json", claim)
        with self.assertRaisesRegex(ValueError, "confirm-stopped"):
            runner.release(self.state, "task-1", False)
        with patch.object(runner, "pid_alive", return_value=True):
            with self.assertRaisesRegex(ValueError, "still alive"):
                runner.release(self.state, "task-1", True)
        with patch.object(runner, "pid_alive", return_value=False):
            with self.assertRaisesRegex(ValueError, "another id"):
                runner.release(self.state, "task-2", True)
            result = runner.release(self.state, "task-1", True)
        self.assertEqual(result["status"], "released")
        self.assertFalse((self.state / "active.json").exists())
        self.assertTrue((self.state / "task-1" / "release.json").exists())

    def test_pid_check_sees_live_process(self):
        self.assertTrue(runner.pid_alive(os.getpid()))

    def test_release_after_crash_before_attempt_directory_creation(self):
        self.state.mkdir()
        runner.atomic_json(self.state / "active.json", {"id": "task-1", "runner_pid": 123, "process_pids": []})
        with patch.object(runner, "pid_alive", return_value=False):
            self.assertEqual(runner.release(self.state, "task-1", True)["status"], "released")
        self.assertTrue((self.state / "task-1" / "release.json").exists())

    def test_claim_persistence_error_terminates_launched_process(self):
        prompt = self.root / "prompt.txt"
        prompt.write_text("task")
        pids = []
        def broken_claim(pid):
            pids.append(pid)
            raise OSError("claim write failure")
        with self.assertRaisesRegex(OSError, "claim write failure"):
            runner.execute([sys.executable, "-c", "import time; time.sleep(30)"], str(self.cwd),
                           prompt, self.root / "process", 10, dict(os.environ), broken_claim)
        self.assertEqual(len(pids), 1)
        self.assertFalse(runner.pid_alive(pids[0]))

    def test_status_reads_receipt_without_worker(self):
        first, _ = self.run_fake()
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), patch.object(runner, "preflight") as preflight:
            code = runner.main(["status", "task-1", "--state-dir", str(self.state)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), first)
        preflight.assert_not_called()

    def test_status_cannot_misattribute_another_active_attempt(self):
        self.state.mkdir()
        runner.atomic_json(self.state / "active.json", {"id": "some-other-task"})
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = runner.main(["status", "task-1", "--state-dir", str(self.state)])
        self.assertEqual(code, 1)
        self.assertIn("No receipt or active claim", json.loads(stdout.getvalue())["error"])

    def test_preflight_uses_read_only_login_status_and_requires_subscription(self):
        version = subprocess.CompletedProcess([], 0, "codex-cli 0.153.4", "")
        auth = subprocess.CompletedProcess([], 0, "", "Logged in using ChatGPT\n")
        with patch.object(runner.subprocess, "run", side_effect=[version, auth]) as call, patch.object(
                runner, "check_shell_cwd") as cwd_check:
            runner.preflight("codex", self.job, {})
        self.assertEqual(call.call_args_list[1].args[0], ["codex", "login", "status"])
        self.assertEqual(cwd_check.call_count, int(os.name == "nt"))
        auth.stderr = "Logged in using an API key"
        with patch.object(runner.subprocess, "run", side_effect=[version, auth]):
            with self.assertRaisesRegex(ValueError, "ChatGPT"):
                runner.preflight("codex", self.job, {})

    def test_shell_cwd_probe_checks_matching_profile_without_model(self):
        for profile in ('edit', 'review'):
            job = dict(self.job, profile=profile)
            with patch.object(runner, 'executable', side_effect=lambda value: value), patch.object(
                    runner.subprocess, 'run', return_value=subprocess.CompletedProcess(
                        [], 0, job['cwd'] + '\n', '')) as call:
                runner.check_shell_cwd('codex.exe', job, {})
            command = call.call_args.args[0]
            self.assertIn(':workspace' if profile == 'edit' else ':read-only', command)
            self.assertNotIn('exec', command)
            self.assertIn('-NoProfile', command)

    def test_shell_cwd_probe_rejects_fallback_empty_and_failed_shell(self):
        for code, output in ((0, str(self.root)), (0, ''), (1, self.job['cwd'])):
            with patch.object(runner, 'executable', side_effect=lambda value: value), patch.object(
                    runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, output, '')):
                with self.assertRaisesRegex(ValueError, 'No worker launched'):
                    runner.check_shell_cwd('codex.exe', self.job, {})


if __name__ == "__main__":
    unittest.main()
