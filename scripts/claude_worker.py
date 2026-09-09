#!/usr/bin/env python3
"""Run bounded Claude Code jobs; stdlib only, no MCP or API-key fallback."""
import argparse
import concurrent.futures
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time


PROFILES = {
    "review": ["Read", "Glob", "Grep"],
    "explore": ["Read", "Glob", "Grep"],
    "edit": ["Read", "Glob", "Grep", "Edit", "Write"],
}


def subscription_env():
    # Preserve Windows runtime variables and local OAuth discovery, not alternate billing.
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("ANTHROPIC_") or key.startswith("CLAUDE_CODE_USE_") or key in {
            "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_API_KEY_HELPER_TTL_MS",
        }:
            del env[key]
    for key in list(env):
        if key.startswith("DISABLE_PROMPT_CACHING"):
            del env[key]
    env["FORCE_PROMPT_CACHING_5M"] = "1"
    return env


def validate(request):
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object")
    jobs = request.get("jobs")
    concurrency = request.get("max_concurrent", 1)
    if type(concurrency) is not int or not 1 <= concurrency <= 4:
        raise ValueError("max_concurrent must be 1..4")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("jobs must be a nonempty array")
    ids = set()
    for job in jobs:
        if not isinstance(job, dict):
            raise ValueError("Each job must be a JSON object")
        for key in ("id", "model", "effort", "profile", "cwd", "prompt"):
            if not isinstance(job.get(key), str) or not job[key].strip():
                raise ValueError(f"Each job requires a nonempty {key}")
        if job["id"] in ids:
            raise ValueError("Job ids must be unique")
        ids.add(job["id"])
        if job["effort"] not in ("low", "medium", "high", "xhigh", "max"):
            raise ValueError("Unsupported effort; use low, medium, high, xhigh, or max")
        if job["profile"] not in PROFILES:
            raise ValueError("profile must be review, explore, or edit")
        if job.get("trusted_context") is not True:
            raise ValueError("Inspect inherited Claude context first, then set trusted_context=true")
        cwd = Path(job["cwd"])
        if not cwd.is_absolute() or not cwd.is_dir():
            raise ValueError("cwd must be an existing absolute directory")
        job["cwd"] = str(cwd.resolve())
        timeout = job.get("timeout_seconds", 1800)
        if type(timeout) is not int or not 1 <= timeout <= 86400:
            raise ValueError("timeout_seconds must be 1..86400")
        if "allow_shell" in job and type(job["allow_shell"]) is not bool:
            raise ValueError("allow_shell must be boolean")
        if job.get("allow_shell") and job["profile"] != "edit":
            raise ValueError("Shell execution requires the edit profile")
        if "session_id" in job and (not isinstance(job["session_id"], str) or not job["session_id"].strip()):
            raise ValueError("session_id must be a nonempty string")
        cap = job.get("max_budget_usd")
        if cap is not None and (type(cap) not in (int, float) or not 0 < cap < float("inf")):
            raise ValueError("max_budget_usd must be finite and positive")
    if concurrency > 1:
        for i, left in enumerate(jobs):
            for right in jobs[i + 1:]:
                if left.get("session_id") and left.get("session_id") == right.get("session_id"):
                    raise ValueError("A resumed session cannot run concurrently with itself")
                a, b = Path(left["cwd"]), Path(right["cwd"])
                overlap = a == b or a in b.parents or b in a.parents
                if overlap and "edit" in (left["profile"], right["profile"]):
                    raise ValueError("Concurrent writes need separate, non-overlapping checkouts")
    return jobs, concurrency


def build_args(binary, job):
    tools = PROFILES[job["profile"]] + (["Bash"] if job.get("allow_shell") else [])
    args = [binary, "-p", "--output-format", "json", "--disable-slash-commands", "--setting-sources", "",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--permission-mode", "dontAsk", "--tools", *tools,
            "--allowedTools", " ".join(tools),
            "--model=" + job["model"], "--effort=" + job["effort"],
            "--append-system-prompt", "Work only on the assigned scope. Do not delegate. "
            "Do not change acceptance criteria. Report complete, partial, or blocked, "
            "with evidence, checks run or skipped, and unresolved risks. "
            "Tool denial or an exhausted budget is not completion. "
            "Read only assignment-relevant evidence and applicable project instructions. "
            "Do not read deployment policies, wrapper code or research references unless they are the assigned subject. "
            "Keep the handoff concise, normally within 200 words; preserve exact failures and decision-critical evidence."]
    if job.get("session_id"):
        args.append("--resume=" + job["session_id"])
    if job.get("max_budget_usd") is not None:
        args += ["--max-budget-usd", str(job["max_budget_usd"])]
    return args


def stop_tree(proc):
    """Return whether the termination operation succeeded; never assume ownership is free."""
    if os.name == "nt":
        result = subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                capture_output=True, timeout=15)
        return result.returncode == 0
    try:
        os.killpg(proc.pid, signal.SIGKILL)
        return True
    except ProcessLookupError:
        return True


def normalize(job, raw, returncode, timed_out=False):
    receipt = {"id": job["id"], "status": "blocked", "requested_model": job["model"],
               "requested_effort": job["effort"], "cwd": job["cwd"],
               "session_id": job.get("session_id"), "exit_code": returncode,
               "timed_out": timed_out}
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")
    except (ValueError, TypeError):
        receipt.update(status="partial" if timed_out else "blocked",
                       error="Missing or invalid CLI JSON; completion and usage are unknown.",
                       raw_output=raw)
        return receipt
    receipt.update(result=data.get("result"), session_id=data.get("session_id", receipt["session_id"]),
                   subtype=data.get("subtype"), usage=data.get("usage"),
                   model_usage=data.get("modelUsage"), estimated_cost_usd=data.get("total_cost_usd"),
                   permission_denials=data.get("permission_denials", []), errors=data.get("errors", []))
    # CLI success means returned, not that the assignment passed acceptance.
    if timed_out or data.get("subtype") in ("error_max_turns", "error_max_budget_usd"):
        receipt["status"] = "partial"
    elif returncode == 0 and data.get("is_error") is False and data.get("subtype") == "success" and not receipt["permission_denials"]:
        receipt["status"] = "returned"
    return receipt


def run_job(binary, job, env):
    started = time.monotonic()
    proc = subprocess.Popen(build_args(binary, job), cwd=job["cwd"], env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace",
                            start_new_session=os.name != "nt")
    timed_out = False
    cleanup = None
    try:
        stdout, stderr = proc.communicate(job["prompt"], timeout=job.get("timeout_seconds", 1800))
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            cleanup = stop_tree(proc)
        except (OSError, subprocess.TimeoutExpired):
            cleanup = False
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            stdout, stderr = "", "Process pipes remain open after attempted termination."
            cleanup = False
    receipt = normalize(job, stdout, proc.returncode, timed_out)
    receipt.update(duration_seconds=round(time.monotonic() - started, 2), stderr=stderr)
    receipt["cli_stdout"] = stdout
    creation = (receipt.get("usage") or {}).get("cache_creation") or {}
    receipt["requested_cache_ttl"] = "5m"
    receipt["cache_ttl_check"] = (
        "mismatch" if creation.get("ephemeral_1h_input_tokens", 0) > 0 else
        "confirmed_5m" if creation.get("ephemeral_5m_input_tokens", 0) > 0 else "unknown")
    if timed_out:
        receipt["termination_succeeded"] = cleanup
        receipt["ownership_check_required"] = True
    return receipt


def compact_receipt(receipt, directory, index):
    """Persist complete evidence before returning a visibly bounded preview."""
    path = Path(directory) / f"job-{index:04d}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
    keys = ("id", "status", "requested_model", "requested_effort", "session_id",
            "exit_code", "timed_out", "duration_seconds", "estimated_cost_usd",
            "termination_succeeded", "ownership_check_required", "cache_ttl_check")
    compact = {key: receipt[key] for key in keys if key in receipt}
    compact["receipt_path"] = str(path.resolve())
    result = receipt.get("result") or ""
    if not isinstance(result, str):
        result = json.dumps(result, ensure_ascii=False)
    compact["result"] = result[:4000]
    compact["result_truncated"] = len(result) > 4000
    compact["details_require_read"] = bool(
        compact["result_truncated"] or receipt.get("status") != "returned" or
        receipt.get("stderr") or receipt.get("errors") or receipt.get("permission_denials") or
        receipt.get("cache_ttl_check") == "mismatch")
    usage = receipt.get("usage") or {}
    compact["tokens"] = {key: usage.get(key) for key in (
        "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}
    compact["reported_models"] = list((receipt.get("model_usage") or {}).keys())
    return compact


def check_cache_support(binary, env):
    result = subprocess.run([binary, "--version"], env=env, capture_output=True,
                            text=True, encoding="utf-8", timeout=20)
    match = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", result.stdout)
    if result.returncode or not match or tuple(map(int, match.groups())) < (2, 1, 108):
        raise ValueError("Five-minute caching requires Claude Code 2.1.108+; update the CLI before running workers.")


def preflight(binary, cwd, env):
    result = subprocess.run([binary, "auth", "status"], cwd=cwd, env=env,
                            capture_output=True, text=True, encoding="utf-8", timeout=20)
    auth = json.loads(result.stdout)
    if result.returncode or not auth.get("loggedIn") or auth.get("authMethod") != "claude.ai" or auth.get("apiProvider") != "firstParty":
        raise ValueError("Requires local Claude.ai subscription login; no billing fallback")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="UTF-8 JSON request file, or - for stdin")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show dispatch; no Claude process")
    parser.add_argument("--claude", default="claude", help="Claude executable path (Windows: native .exe)")
    parser.add_argument("--receipt-dir", help="Existing absolute parent directory for a unique receipt folder; default: system temp")
    options = parser.parse_args()
    try:
        raw = sys.stdin.read() if options.request == "-" else Path(options.request).read_text(encoding="utf-8-sig")
        jobs, concurrency = validate(json.loads(raw))
        binary = shutil.which(options.claude)
        if not binary or (os.name == "nt" and Path(binary).suffix.lower() != ".exe"):
            raise ValueError("Claude executable not found; on Windows provide the native claude.exe")
        if options.dry_run:
            print(json.dumps({"max_concurrent": concurrency, "cache_ttl": "5m", "skills_enabled": False, "jobs": [
                {"id": j["id"], "cwd": j["cwd"], "argv": build_args(binary, j),
                 "prompt_via_stdin": True, "timeout_seconds": j.get("timeout_seconds", 1800)} for j in jobs]}))
            return 0
        env = subscription_env()
        check_cache_support(binary, env)
        # Complete authentication checks before any paid work starts.
        for cwd in dict.fromkeys(j["cwd"] for j in jobs):
            preflight(binary, cwd, env)
        if options.receipt_dir and (not Path(options.receipt_dir).is_absolute() or not Path(options.receipt_dir).is_dir()):
            raise ValueError("--receipt-dir must be an existing absolute directory")
        receipt_dir = tempfile.mkdtemp(prefix="claude-worker-receipts-", dir=options.receipt_dir)
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            stop_dispatch = threading.Event()
            def dispatch(job):
                if stop_dispatch.is_set():
                    return {"id": job["id"], "status": "blocked", "error": "Batch stopped after worker timeout; inspect ownership before continuing."}
                receipt = run_job(binary, job, env)
                if receipt.get("timed_out"):
                    stop_dispatch.set()
                return receipt
            futures = {pool.submit(dispatch, j): (i, j) for i, j in enumerate(jobs)}
            receipts = []
            for future in concurrent.futures.as_completed(futures):
                index, job = futures[future]
                try:
                    receipt = future.result()
                except Exception as exc:
                    receipt = {"id": job["id"], "status": "blocked", "error": str(exc)}
                try:
                    receipts.append(compact_receipt(receipt, receipt_dir, index))
                except OSError as exc:
                    # Do not lose failures or results if evidence cannot be saved.
                    receipt["receipt_write_error"] = str(exc)
                    receipts.append(receipt)
        print(json.dumps({"jobs": receipts}, ensure_ascii=True))
        return 0 if all(r["status"] == "returned" for r in receipts) else 1
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
