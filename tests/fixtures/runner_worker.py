"""Offline CLI fixture. Never imports or launches an agent CLI."""
import json
from pathlib import Path
import sys
import time

sys.stdin.reconfigure(encoding="utf-8")
provider, mode, folder = sys.argv[1:]
root = Path(folder)
prompt = sys.stdin.read()
(root / "fixture-stdin.txt").write_text(prompt, encoding="utf-8")
if mode == "timeout":
    if provider == "codex":
        print(json.dumps({"type": "thread.started", "thread_id": "codex-fixture-session"}), flush=True)
    print("partial evidence before timeout", flush=True)
    time.sleep(30)
    sys.exit(0)
handoff = {"status": mode if mode in {"partial", "blocked"} else "complete",
           "summary": "Read source and preserved the requested behavior.",
           "artifacts": ["result.txt"], "checks": [], "risks": []}
Path("result.txt").write_text("unchanged contract\n", encoding="utf-8")
if mode == "tamper":
    Path("checker.py").write_text("# weakened check\n", encoding="utf-8")
if mode == "verbose":
    handoff["summary"] = "private evidence " * 10000
if mode == "missing_artifact":
    handoff["artifacts"].append("missing.txt")
if mode == "outside_artifact":
    handoff["artifacts"].append("../outside.txt")
if provider == "claude":
    data = {"subtype": "success", "is_error": False, "session_id": "claude-fixture-session",
            "structured_output": handoff, "usage": {"input_tokens": 100, "output_tokens": 20},
            "modelUsage": {"claude-opus-5": {"inputTokens": 100}}, "total_cost_usd": 0.01}
    if mode == "limit":
        data.update(subtype="error_max_budget_usd", is_error=True)
    elif mode == "denied":
        data["permission_denials"] = [{"tool_name": "Write"}]
    elif mode == "malformed":
        data["structured_output"] = {"status": "complete"}
    elif mode == "cache_mismatch":
        data["usage"]["cache_creation"] = {"ephemeral_1h_input_tokens": 100}
    elif mode == "bad_usage":
        data["usage"] = "not telemetry"
    print(json.dumps(data))
else:
    print(json.dumps({"type": "thread.started", "thread_id": "codex-fixture-session"}))
    (root / "handoff.json").write_text(json.dumps(handoff), encoding="utf-8")
    if mode == "malformed":
        print("not json")
    elif mode == "error":
        print(json.dumps({"type": "turn.failed", "error": {"message": "fixture failure"}}))
    elif mode != "missing_completion":
        print(json.dumps({"type": "turn.completed", "usage": {
            "input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 20}}))
    if mode == "multiple_turns":
        print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 999}}))
if mode == "nonzero":
    sys.exit(4)
