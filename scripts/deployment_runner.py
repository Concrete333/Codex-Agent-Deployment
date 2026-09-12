#!/usr/bin/env python3
"""One bounded worker attempt and predefined checks; no model-owned scheduling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import sys
import time

import claude_worker


SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["complete", "partial", "blocked"]},
        "summary": {"type": "string"},
        **{key: {"type": "array", "items": {"type": "string"}}
           for key in ("artifacts", "checks", "risks")},
    },
    "required": ["status", "summary", "artifacts", "checks", "risks"],
}
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
MODELS = {"gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_json(path, value):
    # Only this runner owns these paths; refuse another runner through the claim.
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode("utf-8")).hexdigest()


def within(path, root):
    return path == root or root in path.parents


def absolute_directory(value, label, existing=True):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError(f"{label} must be an absolute directory")
    path = Path(value).resolve()
    if existing and not path.is_dir():
        raise ValueError(f"{label} must exist")
    return path


def artifact_path(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError("artifacts must name relative files inside cwd, without '..'")
    path = (root / name).resolve()
    if not within(path, root) or path == root or path.is_dir():
        raise ValueError(f"Artifact is outside cwd or is not a file: {name}")
    return path


def validate(raw):
    if not isinstance(raw, dict):
        raise ValueError("Request must be an object")
    job = json.loads(json.dumps(raw, allow_nan=False))
    allowed = {"id", "provider", "model", "effort", "cwd", "prompt", "profile",
               "trusted_context", "timeout_seconds", "artifacts", "checks",
               "allow_shell", "max_budget_usd", "protected_files"}
    if set(job) - allowed:
        raise ValueError("Unknown request fields: " + ", ".join(sorted(set(job) - allowed)))
    for key in ("id", "provider", "model", "effort", "cwd", "prompt", "profile"):
        if not isinstance(job.get(key), str) or not job[key].strip():
            raise ValueError(f"Nonempty {key} required")
    if not ID.fullmatch(job["id"]):
        raise ValueError("id must use 1..64 letters, digits, underscores or hyphens")
    root = absolute_directory(job["cwd"], "cwd")
    job["cwd"] = str(root)
    if job.get("trusted_context") is not True:
        raise ValueError("Inspect checkout and inherited CLI context, then set trusted_context=true")
    if type(job.get("timeout_seconds")) is not int or not 1 <= job["timeout_seconds"] <= 86400:
        raise ValueError("An explicit timeout_seconds in 1..86400 is required")
    if job["effort"] not in EFFORTS or job["profile"] not in {"review", "explore", "edit"}:
        raise ValueError("Unsupported effort or profile")
    if job["provider"] == "codex":
        if job["model"] not in MODELS or (job["model"] == "gpt-5.6-luna" and job["effort"] != "max"):
            raise ValueError("Codex workers: Luna Max, Terra or Sol only")
        if "allow_shell" in job or "max_budget_usd" in job:
            raise ValueError("allow_shell and max_budget_usd are Claude-only fields")
    elif job["provider"] == "claude":
        claude_worker.validate({"jobs": [job]})
    else:
        raise ValueError("provider must be codex or claude")
    if not isinstance(job.get("artifacts"), list) or not isinstance(job.get("checks"), list):
        raise ValueError("Explicit artifacts and checks arrays required (may be empty)")
    for name in job["artifacts"]:
        artifact_path(root, name)
    if len(set(job["artifacts"])) != len(job["artifacts"]):
        raise ValueError("Duplicate artifacts")
    protected = job.setdefault("protected_files", [])
    if not isinstance(protected, list):
        raise ValueError("protected_files must be an array of existing file paths")
    for index, name in enumerate(protected):
        if not isinstance(name, str) or not name or ".." in Path(name).parts:
            raise ValueError("Invalid protected file path")
        path = (root / name).resolve()
        if not path.is_file():
            raise ValueError(f"Protected file must exist: {name}")
        protected[index] = str(path)
    seen = set()
    for check in job["checks"]:
        if not isinstance(check, dict) or set(check) != {"id", "argv", "timeout_seconds"}:
            raise ValueError("Each check requires exactly id, argv, timeout_seconds")
        if not isinstance(check["id"], str) or not ID.fullmatch(check["id"]) or check["id"] in seen:
            raise ValueError("Check ids must be valid and unique")
        seen.add(check["id"])
        argv = check["argv"]
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or "\x00" in a for a in argv):
            raise ValueError("Check argv must be a nonempty array of strings without NULs")
        executable(argv[0])  # Reject invalid programs before paying for a worker.
        if type(check["timeout_seconds"]) is not int or not 1 <= check["timeout_seconds"] <= 86400:
            raise ValueError("Each check requires timeout_seconds in 1..86400")
    return job


def executable(value):
    found = shutil.which(value)
    if not found or (os.name == "nt" and Path(found).suffix.lower() != ".exe"):
        raise ValueError(f"Executable not found (Windows requires native .exe): {value}")
    return str(Path(found).resolve())


def worker_env(provider):
    if provider == "claude":
        return claude_worker.subscription_env()
    # Preserve OS runtime/login discovery, not the host's unrelated secrets or interpreter hooks.
    keep = {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "USERPROFILE",
            "APPDATA", "LOCALAPPDATA", "HOMEDRIVE", "HOMEPATH", "COMSPEC", "OS",
            "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432", "PROGRAMDATA",
            "ALLUSERSPROFILE", "PUBLIC", "USERNAME", "USERDOMAIN", "USERDOMAIN_ROAMINGPROFILE",
            "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "PROCESSOR_IDENTIFIER",
            "HOME", "CODEX_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
            "TERM", "COLORTERM", "LANG", "LC_ALL", "LC_CTYPE", "TZ"}
    return {key: value for key, value in os.environ.items() if key.upper() in keep}


def preflight(binary, job, env):
    if job["provider"] == "claude":
        claude_worker.check_cache_support(binary, env)
        claude_worker.preflight(binary, job["cwd"], env)
        return
    result = subprocess.run([binary, "--version"], capture_output=True, text=True,
                            encoding="utf-8", timeout=20, env=env)
    version = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", result.stdout)
    if result.returncode or not version or tuple(map(int, version.groups())) < (0, 153, 4):
        raise ValueError("This adapter requires Codex CLI 0.153.4+; unsupported flags fail closed")
    result = subprocess.run([binary, "login", "status"],
                            capture_output=True, text=True, encoding="utf-8", timeout=20, env=env)
    if result.returncode or (result.stdout + result.stderr).strip() != "Logged in using ChatGPT":
        raise ValueError("Requires local ChatGPT login; no API-key billing fallback")
    if os.name == "nt":
        check_shell_cwd(binary, job, env)


def check_shell_cwd(binary, job, env):
    """Fail before a model call if the Windows sandbox loses the checkout cwd."""
    command = build_check(binary, job, {"argv": ["powershell.exe", "-NoProfile",
        "-NonInteractive", "-Command", "$ErrorActionPreference='Stop'; (Get-Location).ProviderPath"]})
    result = subprocess.run(command, cwd=job["cwd"], env=env, capture_output=True,
                            text=True, encoding="utf-8", timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    actual = result.stdout.strip()
    if (result.returncode or not actual or
            os.path.normcase(os.path.normpath(actual)) !=
            os.path.normcase(os.path.normpath(job["cwd"]))):
        raise ValueError(f"Sandbox shell cwd preflight failed: expected {job['cwd']!r}, "
                         f"observed {actual!r}, exit {result.returncode}. "
                         "No worker launched; repair checkout access before retrying. " + result.stderr.strip())


def build_worker(binary, job, folder):
    if job["provider"] == "claude":
        return claude_worker.build_args(binary, job) + ["--json-schema", json.dumps(SCHEMA)]
    args = [binary, "exec", "--ignore-user-config", "--ignore-rules", "--strict-config",
            "--json", "--color", "never", "--sandbox",
            "workspace-write" if job["profile"] == "edit" else "read-only",
            "--model", job["model"], "--cd", job["cwd"],
            "--output-schema", str(folder / "handoff-schema.json"),
            "--output-last-message", str(folder / "handoff.json")]
    config = {
        "model_provider": "openai", "model_reasoning_effort": job["effort"], "approval_policy": "never",
        "agents.enabled": False, "features.multi_agent": False,
        "features.multi_agent_v2.enabled": False, "features.plugins": False,
        "features.remote_plugin": False, "features.memories": False,
        "memories.use_memories": False, "memories.generate_memories": False,
        "web_search": "disabled", "mcp_servers": {},
    }
    if os.name == "nt":
        config["windows.sandbox"] = "elevated"
    for key, value in config.items():
        args += ["-c", f"{key}={json.dumps(value)}"]
    return args + ["-"]


def prompt_for(job):
    check_ids = ", ".join(c["id"] for c in job["checks"]) or "none"
    protected = "; ".join(job.get("protected_files", [])) or "none declared"
    return (job["prompt"] + "\n\nExecution contract: Own only this assignment. Do not delegate, change "
            "acceptance criteria, or leave background commands running. Read applicable project instructions "
            "and assignment evidence, not routing guides or research. Return JSON matching the supplied schema: "
            "status complete|partial|blocked, a concise summary, artifacts, checks and unresolved risks. "
            "List artifacts as relative file paths inside the checkout, without descriptions. "
            "Completion is your report, not acceptance. Preserve exact failures and flag judgment calls. "
            f"The runner owns these final objective checks: {check_ids}. Do not repeat them solely for handoff; "
            "run local checks when needed to develop or correct your work. "
            f"Do not edit protected files: {protected}.")


def build_check(binary, job, check):
    command = [executable(check["argv"][0]), *check["argv"][1:]]
    if job["provider"] != "codex":
        return command
    args = [binary, "sandbox", "-P", ":workspace" if job["profile"] == "edit" else ":read-only",
            "-C", job["cwd"], "-c", 'approval_policy="never"']
    if os.name == "nt":
        args += ["-c", 'windows.sandbox="elevated"']
    return args + ["--", *command]


def execute(argv, cwd, stdin_path, prefix, timeout, env, on_start):
    started = time.monotonic()
    proc = None
    result = {"argv": argv, "stdout_path": str(prefix) + ".stdout",
              "stderr_path": str(prefix) + ".stderr", "timed_out": False,
              "ownership_check_required": False}
    with open(result["stdout_path"], "wb") as out, open(result["stderr_path"], "wb") as err:
        with open(stdin_path, "rb") as source:
            try:
                proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=source, stdout=out, stderr=err,
                                        start_new_session=os.name != "nt")
                on_start(proc.pid)
                proc.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
                result["timed_out"] = isinstance(exc, subprocess.TimeoutExpired)
                result["interrupted"] = isinstance(exc, KeyboardInterrupt)
                result["ownership_check_required"] = True
                try:
                    result["termination_succeeded"] = claude_worker.stop_tree(proc) if proc else True
                    if proc:
                        proc.wait(timeout=10)
                except (OSError, subprocess.SubprocessError):
                    result["termination_succeeded"] = False
            except BaseException:
                # A receipt or claim write can fail after launch. Never leave an untracked writer willingly.
                if proc:
                    try:
                        claude_worker.stop_tree(proc)
                        proc.wait(timeout=10)
                    except (OSError, subprocess.SubprocessError):
                        pass
                raise
    result.update(pid=proc.pid if proc else None, exit_code=proc.returncode if proc else None,
                  duration_seconds=round(time.monotonic() - started, 3))
    return result


def validate_handoff(data):
    if not isinstance(data, dict) or set(data) != set(SCHEMA["required"]):
        raise ValueError("Missing or invalid structured handoff")
    if data["status"] not in {"complete", "partial", "blocked"} or not isinstance(data["summary"], str) or not data["summary"].strip():
        raise ValueError("Invalid handoff status or empty summary")
    for key in ("artifacts", "checks", "risks"):
        if not isinstance(data[key], list) or any(not isinstance(x, str) for x in data[key]):
            raise ValueError(f"Invalid handoff {key}")
    return data


def parse_worker(job, folder, process):
    meta = {"session_id": None, "usage": None, "reported_models": [], "effective_effort": "unknown"}
    if job["provider"] == "claude":
        data = read_json(process["stdout_path"])
        if not isinstance(data, dict):
            raise ValueError("Invalid Claude result")
        for field in ("usage", "modelUsage"):
            if data.get(field) is not None and not isinstance(data[field], dict):
                raise ValueError(f"Invalid Claude {field}")
        if (data.get("usage") or {}).get("cache_creation") is not None and not isinstance(data["usage"]["cache_creation"], dict):
            raise ValueError("Invalid Claude cache creation telemetry")
        meta.update(session_id=data.get("session_id"), usage=data.get("usage"),
                    model_usage=data.get("modelUsage"), reported_models=list((data.get("modelUsage") or {}).keys()),
                    estimated_cost_usd=data.get("total_cost_usd"))
        creation = (data.get("usage") or {}).get("cache_creation") or {}
        meta["cache_ttl_check"] = ("mismatch" if creation.get("ephemeral_1h_input_tokens", 0) else
                                   "confirmed_5m" if creation.get("ephemeral_5m_input_tokens", 0) else "unknown")
        if data.get("subtype") in {"error_max_turns", "error_max_budget_usd"}:
            return None, meta, "partial"
        if process["exit_code"] or data.get("is_error") is not False or data.get("subtype") != "success" or data.get("permission_denials"):
            return None, meta, "blocked"
        handoff = validate_handoff(data.get("structured_output"))
        atomic_json(folder / "handoff.json", handoff)
        return handoff, meta, handoff["status"]
    turns, errors = [], []
    with open(process["stdout_path"], encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("Invalid Codex event")
            kind = event.get("type")
            if kind == "thread.started":
                meta["session_id"] = event.get("thread_id")
            elif kind == "turn.completed":
                turns.append(event.get("usage"))
            elif kind in {"error", "turn.failed"}:
                errors.append(event)
    meta["usage"] = turns[0] if len(turns) == 1 else None
    meta["turn_usages"] = turns
    meta["errors"] = errors
    # This adapter launches exactly one turn. Never reinterpret abnormal event streams as success.
    if process["exit_code"] or errors or len(turns) != 1 or not meta["session_id"]:
        return None, meta, "blocked"
    handoff = validate_handoff(read_json(folder / "handoff.json"))
    return handoff, meta, handoff["status"]


def interrupted_codex_session(path):
    """Recover identity, not success or complete usage, from an interrupted event stream."""
    identities = set()
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict) and event.get("type") == "thread.started":
                identity = event.get("thread_id")
                if isinstance(identity, str) and identity:
                    identities.add(identity)
    return next(iter(identities)) if len(identities) == 1 else None


def hash_files(paths):
    result = {}
    for name, path in paths.items():
        # Streaming hashing is available in Python 3.10 as well as newer versions.
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
        result[name] = hasher.hexdigest()
    return result


def artifact_hashes(job, names, binary=None):
    names = list(names)
    try:
        paths = {name: artifact_path(Path(job["cwd"]), name) for name in names}
        return hash_files(paths)
    except PermissionError:
        if job['provider'] != 'codex' or not binary:
            raise
        # A sandbox-created Windows file can be readable in that sandbox but not by the host.
        # Do not change ACLs, omit the file, or run a model to hash it.
        command = build_check(binary, dict(job, profile='review'), {'argv': [sys.executable,
            '-I', '-B', str(Path(__file__).with_name('deployment_hash.py'))]})
        observed = subprocess.run(command, cwd=job['cwd'], env=worker_env('codex'),
            input=json.dumps({'root': job['cwd'], 'names': names}), capture_output=True,
            text=True, encoding='utf-8', timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        if observed.returncode:
            raise ValueError('Sandbox artifact hashing failed: ' + observed.stderr)
        hashes = json.loads(observed.stdout)
        if (not isinstance(hashes, dict) or set(hashes) != set(names)
                or any(not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value)
                       for value in hashes.values())):
            raise ValueError('Invalid sandbox artifact hashes')
        return hashes


def fingerprints(job, binary=None):
    return artifact_hashes(job, job['artifacts'], binary)


def handoff_fingerprints(job, handoff, binary=None):
    return artifact_hashes(job, handoff['artifacts'], binary)


def review_gate(job, state, binary=None):
    """Revalidate a terminal attempt before a caller spends on acceptance. No model calls."""
    folder = state / job["id"]
    receipt = read_json(folder / "receipt.json")
    handoff = read_json(folder / "handoff.json")
    return verify_review_evidence(job, receipt, handoff, binary)


def verify_review_evidence(job, receipt, handoff, binary=None):
    """Validate saved observations; callers own their provenance and exclusive write access."""
    if (receipt.get("id") != job["id"] or receipt.get("request_sha256") != digest(job)
            or receipt.get("status") != "ready_for_review" or receipt.get("ownership_check_required")):
        raise ValueError("Attempt is not ready for acceptance review")
    handoff = validate_handoff(handoff)
    if handoff["status"] != "complete":
        raise ValueError("Handoff is not complete")
    expected = [(check["id"], "passed") for check in job["checks"]]
    if [(check.get("id"), check.get("status")) for check in receipt.get("checks", [])] != expected:
        raise ValueError("Required checks did not pass")
    if (receipt.get("artifact_sha256") != fingerprints(job, binary)
            or receipt.get("artifact_sha256_after_checks") != fingerprints(job, binary)
            or receipt.get("handoff_artifact_sha256") != handoff_fingerprints(job, handoff, binary)
            or receipt.get("protected_sha256") != protected_hashes(job)):
        raise ValueError("Evidence changed or is missing before acceptance review")
    return receipt, handoff


def protected_hashes(job):
    return hash_files({name: Path(name) for name in job.get("protected_files", [])})


def compact(receipt, folder):
    return {"id": receipt["id"], "status": receipt["status"], "accepted": False,
            "receipt_path": str(folder / "receipt.json") if (folder / "receipt.json").exists() else None,
            "handoff_path": str(folder / "handoff.json") if (folder / "handoff.json").exists() else None,
            "checks": [{"id": check["id"], "status": check["status"]} for check in receipt.get("checks", [])],
            "ownership_check_required": receipt.get("ownership_check_required", False),
            "error": receipt.get("error"), "usage": receipt.get("worker", {}).get("usage"),
            "estimated_cost_usd": receipt.get("worker", {}).get("estimated_cost_usd")}


def run(job, state, binary, dry_run=False, *, expected_protected=None):
    started_at = time.time()
    if within(state, Path(job["cwd"])) or within(Path(job["cwd"]), state):
        raise ValueError("Keep the private state directory separate from the worker checkout")
    folder = state / job["id"]
    argv = build_worker(binary, job, folder)
    if dry_run:
        return {"status": "dry_run", "argv": argv, "prompt_via_stdin": True,
                "timeout_seconds": job["timeout_seconds"], "checks": job["checks"],
                "state_dir": str(state), "paid_calls": 0}
    fingerprint = digest(job)
    # Same id + same request returns the original result; never silently spends again.
    if folder.exists():
        if not (folder / "request.json").exists() or digest(read_json(folder / "request.json")) != fingerprint:
            raise ValueError("Existing id has different or incomplete state; inspect it, then use a new id")
        if (folder / "receipt.json").exists():
            return compact(read_json(folder / "receipt.json"), folder)
        raise ValueError("Attempt already running or interrupted; inspect state, do not redispatch")
    state.mkdir(parents=True, exist_ok=True)
    claim_path = state / "active.json"
    claim = {"id": job["id"], "runner_pid": os.getpid(), "process_pids": [],
             "phase": "preflight", "cwd": job["cwd"], "request_sha256": fingerprint}
    try:
        with claim_path.open("x", encoding="utf-8") as stream:
            json.dump(claim, stream)
    except FileExistsError:
        raise ValueError("State directory has an active or unresolved attempt; inspect active.json") from None
    receipt = {"id": job["id"], "status": "blocked", "accepted": False,
               "request_sha256": fingerprint, "requested_model": job["model"],
               "requested_effort": job["effort"], "checks": [], "ownership_check_required": False,
               "started_at_unix": started_at}
    release_claim = False
    try:
        folder.mkdir()
        atomic_json(folder / "request.json", job)
        atomic_json(folder / "handoff-schema.json", SCHEMA)
        (folder / "prompt.txt").write_text(prompt_for(job), encoding="utf-8")
        (folder / "empty-stdin.txt").write_text("", encoding="utf-8")
        atomic_json(folder / "worker-command.json", argv)
        receipt["protected_sha256"] = dict(expected_protected) if expected_protected is not None else protected_hashes(job)
        if receipt["protected_sha256"] != protected_hashes(job):
            raise ValueError("Protected files differ from the authorized baseline; no worker started")
        env = worker_env(job["provider"])
        preflight(binary, job, env)

        def started(pid):
            claim["process_pids"].append(pid)
            atomic_json(claim_path, claim)

        claim["phase"] = "worker"
        process = execute(argv, job["cwd"], folder / "prompt.txt", folder / "worker",
                          job["timeout_seconds"], env, started)
        receipt["worker_process"] = process
        if process["ownership_check_required"]:
            receipt.update(status="partial", ownership_check_required=True)
            if job["provider"] == "codex":
                receipt["worker"] = {"session_id": interrupted_codex_session(process["stdout_path"]),
                                     "usage": None, "effective_effort": "unknown",
                                     "usage_note": "Interrupted: inspect rollout; in-flight usage may be missing"}
        else:
            handoff, metadata, status = parse_worker(job, folder, process)
            receipt["worker"] = metadata
            receipt["status"] = status
            release_claim = True
            if handoff and status == "complete":
                if receipt["protected_sha256"] != protected_hashes(job):
                    raise ValueError("Protected evidence/checker changed during worker execution; do not trust a pass")
                receipt["artifact_sha256"] = fingerprints(job, binary)
                receipt["handoff_artifact_sha256"] = handoff_fingerprints(job, handoff, binary)
                claim["phase"] = "checks"
                for check in job["checks"]:
                    command = build_check(binary, job, check)
                    result = execute(command, job["cwd"], folder / "empty-stdin.txt",
                                     folder / ("check-" + check["id"]), check["timeout_seconds"],
                                     dict(worker_env(job["provider"]), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"), started)
                    result.update(id=check["id"], status="passed" if result["exit_code"] == 0 and not result["ownership_check_required"] else "failed")
                    receipt["checks"].append(result)
                    if result["ownership_check_required"]:
                        receipt.update(status="partial", ownership_check_required=True)
                        release_claim = False
                        break
                else:
                    receipt["artifact_sha256_after_checks"] = fingerprints(job, binary)
                    if receipt["artifact_sha256"] != receipt["artifact_sha256_after_checks"]:
                        raise ValueError("Declared artifacts changed during checks; review and revalidate the new bytes")
                    if receipt["handoff_artifact_sha256"] != handoff_fingerprints(job, handoff, binary):
                        raise ValueError("Handoff artifacts changed during checks")
                    if receipt["protected_sha256"] != protected_hashes(job):
                        raise ValueError("Protected evidence/checker changed during checks; do not trust a pass")
                    receipt["status"] = "checks_failed" if any(c["status"] == "failed" for c in receipt["checks"]) else "ready_for_review"
    except (OSError, ValueError, TypeError, subprocess.SubprocessError, KeyboardInterrupt) as exc:
        receipt.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        # No automatic recovery after an exception once any process has been launched.
        receipt["ownership_check_required"] = bool(claim["process_pids"])
        release_claim = not receipt["ownership_check_required"]
    finally:
        # If persistence itself fails, leave the claim in place.
        receipt["finished_at_unix"] = time.time()
        receipt["duration_seconds"] = round(receipt["finished_at_unix"] - started_at, 3)
        receipt["runner_pid"] = claim["runner_pid"]
        receipt["process_pids"] = claim["process_pids"]
        if folder.is_dir():
            atomic_json(folder / "receipt.json", receipt)
        if release_claim:
            claim_path.unlink()
    return compact(receipt, folder)


def pid_alive(pid):
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87  # Access denied or unknown: assume alive.
        try:
            code = wintypes.DWORD()
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def release(state, run_id, confirmed):
    if not confirmed:
        raise ValueError("Inspect descendants and shared resources, then pass --confirm-stopped")
    claim = read_json(state / "active.json")
    if claim["id"] != run_id:
        raise ValueError("Active claim belongs to another id")
    if any(pid_alive(pid) for pid in [claim["runner_pid"], *claim["process_pids"]]):
        raise ValueError("A recorded process is still alive (or its PID was reused); do not release ownership")
    (state / run_id).mkdir(exist_ok=True)  # A crash can occur just after claiming, before creating the attempt folder.
    atomic_json(state / run_id / "release.json", {"id": run_id, "confirmed_stopped": True,
                                                 "time_unix": time.time(), "claim": claim})
    (state / "active.json").unlink()
    return {"id": run_id, "status": "released", "original_receipt_unchanged": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "status", "release"))
    parser.add_argument("target", help="Request JSON (run), or attempt id (status/release)")
    parser.add_argument("--state-dir", required=True, help="Absolute private directory, shared by all runner calls")
    parser.add_argument("--codex", default="codex", help="Native Codex executable")
    parser.add_argument("--claude", default="claude", help="Native Claude executable")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm-stopped", action="store_true")
    options = parser.parse_args(argv)
    try:
        state = absolute_directory(options.state_dir, "state-dir", existing=False)
        if options.action == "run":
            job = validate(read_json(options.target))
            binary = executable(options.codex if job["provider"] == "codex" else options.claude)
            result = run(job, state, binary, options.dry_run)
        else:
            if not ID.fullmatch(options.target) or options.dry_run:
                raise ValueError("status/release require a valid id; --dry-run is for run only")
            if options.action == "release":
                result = release(state, options.target, options.confirm_stopped)
            else:
                folder = state / options.target
                if (folder / "receipt.json").exists():
                    result = compact(read_json(folder / "receipt.json"), folder)
                else:
                    claim = read_json(state / "active.json")
                    if claim["id"] != options.target:
                        raise ValueError("No receipt or active claim for that id")
                    result = {"id": options.target, "status": "unfinished_or_interrupted", "active": claim}
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0 if result["status"] in {"ready_for_review", "dry_run", "released"} else 1
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "error": f"{type(exc).__name__}: {exc}"}))
        return 1


def interrupt_handler(*_):
    raise KeyboardInterrupt()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupt_handler)
    sys.exit(main())
