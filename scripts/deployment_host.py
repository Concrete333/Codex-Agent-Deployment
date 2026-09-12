#!/usr/bin/env python3
"""One-shot, host-authorized Codex dispatch. The sandbox client can only trigger a frozen job."""
import argparse
import json
import os
from pathlib import Path
import secrets
import signal
import sys
import time

import deployment_runner as runner


def bounded_json(path):
    # The bridge is untrusted input, not a channel for arbitrary job descriptions.
    with Path(path).open("rb") as stream:
        raw = stream.read(8193)
    if len(raw) > 8192:
        raise ValueError("Bridge message exceeds 8 KiB")
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Bridge message must be an object")
    return data


def disjoint(a, b, *, inspect_ancestors=True):
    if not inspect_ancestors:
        return not runner.within(a.resolve(), b.resolve()) and not runner.within(b.resolve(), a.resolve()) and not a.samefile(b)
    def contains(parent, child):
        if runner.within(child.resolve(), parent.resolve()):
            return True
        return parent.exists() and any(p.exists() and parent.samefile(p) for p in (child, *child.parents))
    return not contains(a, b) and not contains(b, a)


SLOT_SIZE = 8192


def read_trigger(stream):
    stream.seek(0, os.SEEK_END)
    if stream.tell() != SLOT_SIZE + 1:
        raise ValueError("Trigger must have an 8 KiB payload and one publish byte")
    stream.seek(SLOT_SIZE)
    flag = stream.read(1)
    if flag == b"0":
        return None
    if flag != b"1":
        raise ValueError("Invalid trigger publish byte")
    stream.seek(0)
    return json.loads(stream.read(SLOT_SIZE).decode("utf-8"))


def publish_trigger(path, data):
    raw = json.dumps(data).encode("utf-8")
    if len(raw) > SLOT_SIZE:
        raise ValueError("Trigger exceeds 8 KiB")
    # Update the host-owned file in place: replacement changes Windows ownership.
    with Path(path).open("r+b", buffering=0) as stream:
        existing = read_trigger(stream)
        if existing is not None:
            if existing != data:
                raise ValueError("Another or altered trigger is present")
            return
        stream.seek(0)
        stream.write(raw.ljust(SLOT_SIZE, b" "))
        os.fsync(stream.fileno())
        stream.seek(SLOT_SIZE)
        stream.write(b"1")
        os.fsync(stream.fileno())


def duration(value):
    if type(value) is not int or not 1 <= value <= 86400:
        raise ValueError("Timeout must be an integer in 1..86400 seconds")
    return value


def trigger_data(ticket):
    return {key: ticket[key] for key in ("id", "token", "request_sha256")}


def serve(raw_job, state, bridge, binary, trigger_timeout, on_ready=print):
    """Invoked by the authenticated host, never by the sandboxed client."""
    job = runner.validate(raw_job)  # Detached normalized copy: caller cannot mutate the accepted job.
    state, bridge = state.resolve(), bridge.resolve()
    if job["provider"] != "codex":
        raise ValueError("The host bridge supports Codex workers only")
    duration(trigger_timeout)
    root = Path(job["cwd"])
    if not disjoint(state, root) or not disjoint(state, bridge):
        raise ValueError("Private state must be outside the checkout and shared bridge")
    for script in (Path(__file__).resolve(), Path(runner.__file__).resolve()):
        if runner.within(script, root) or runner.within(script, bridge):
            raise ValueError("Keep host scripts outside the worker/client writable directories")
    binary = runner.executable(binary)
    if runner.within(Path(binary), root) or runner.within(Path(binary), bridge):
        raise ValueError("Codex executable must be outside the worker/client writable directories")
    if (state / "active.json").exists() or (state / job["id"]).exists():
        raise ValueError("An active or existing attempt must be inspected, not re-armed")
    env = runner.worker_env("codex")
    runner.preflight(binary, job, env)  # No model calls, and no ticket if authentication fails.
    protected = runner.protected_hashes(job)
    ticket_dir = state / ".host-tickets" / job["id"]
    ticket_dir.mkdir(parents=True, exist_ok=False)  # Durable guard against re-arming after crash/restart.
    bridge.mkdir(parents=True, exist_ok=True)
    if not disjoint(state, root) or not disjoint(state, bridge):
        raise ValueError("Private state must be outside the checkout and shared bridge")
    token = secrets.token_hex(24)
    trigger = bridge / (job["id"] + "-" + token + ".trigger.json")
    slot = trigger.open("x+b", buffering=0)
    slot.write(b" " * SLOT_SIZE + b"0")
    os.fsync(slot.fileno())
    ticket = {"id": job["id"], "token": token, "request_sha256": runner.digest(job),
              "trigger_path": str(trigger), "result_path": str(ticket_dir / "result.json"),
              "trigger_expires_at": time.time() + trigger_timeout}
    ticket_path = ticket_dir / "ticket.json"
    runner.atomic_json(ticket_dir / "authorized-request.json", job)
    runner.atomic_json(ticket_path, ticket)
    runner.atomic_json(ticket_dir / "host.json", {"pid": os.getpid(), "binary": binary,
                                                 "protected_sha256": protected})
    result = {"id": job["id"], "status": "blocked", "accepted": False, "worker_started": False}
    try:
        on_ready({"status": "armed", "ticket_path": str(ticket_path),
                  "id": job["id"], "request_sha256": ticket["request_sha256"]})
        deadline = time.monotonic() + trigger_timeout
        data = read_trigger(slot)
        while data is None:
            if time.monotonic() >= deadline:
                raise TimeoutError("No trigger before the host's dispatch deadline; no worker started")
            time.sleep(0.1)  # Ordinary software waits; no model polling or scheduler automation.
            data = read_trigger(slot)
        if trigger.is_symlink() or trigger.resolve() != trigger:
            raise ValueError("Trigger must be a regular file at its authorized path")
        if time.monotonic() >= deadline or data != trigger_data(ticket):
            raise ValueError("Expired or altered trigger; no worker started")
        if runner.protected_hashes(job) != protected:
            raise ValueError("Protected files changed after host authorization; no worker started")
        runner.atomic_json(ticket_dir / "dispatch.json", {"time_unix": time.time(),
                                                         "request_sha256": ticket["request_sha256"]})
        result = runner.run(job, state, binary, expected_protected=protected)
        receipt_path = state / job["id"] / "receipt.json"
        result["worker_started"] = bool(runner.read_json(receipt_path).get("process_pids")) if receipt_path.exists() else False
    except (OSError, ValueError, TypeError, KeyboardInterrupt) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["ownership_check_required"] = (state / "active.json").exists()
    finally:
        slot.close()
        # This location is not writable by the sandbox caller. Shared bridge files are never receipts.
        result["request_sha256"] = ticket["request_sha256"]
        runner.atomic_json(Path(ticket["result_path"]), result)
    return result


def request(ticket_path, wait_seconds):
    """No CLI, model, credential or arbitrary host-command access from this client."""
    duration(wait_seconds)
    ticket_path = Path(ticket_path).resolve(strict=True)
    ticket = bounded_json(ticket_path)
    required = {"id", "token", "request_sha256", "trigger_path", "result_path", "trigger_expires_at"}
    if set(ticket) != required or not runner.ID.fullmatch(ticket["id"]):
        raise ValueError("Invalid host ticket")
    if not isinstance(ticket["token"], str) or len(ticket["token"]) != 48 or any(c not in "0123456789abcdef" for c in ticket["token"]):
        raise ValueError("Invalid host ticket token")
    if not isinstance(ticket["request_sha256"], str) or len(ticket["request_sha256"]) != 64:
        raise ValueError("Invalid request digest")
    trigger, result_path = Path(ticket["trigger_path"]), Path(ticket["result_path"])
    if not trigger.is_absolute() or not result_path.is_absolute() or result_path.name != "result.json" or not result_path.parent.samefile(ticket_path.parent):
        raise ValueError("Invalid ticket paths")
    # Windows packaged apps can expose two different spellings of the same LocalAppData directory.
    result_path = ticket_path.parent / "result.json"
    # The host already checked ancestry before publishing this private ticket.
    # A sandbox may access the endpoints but be unable to stat their parents.
    if not disjoint(ticket_path.parent, trigger.parent, inspect_ancestors=False) or trigger.name != ticket["id"] + "-" + ticket["token"] + ".trigger.json":
        raise ValueError("Invalid trigger location")

    def result_if_ready():
        if not result_path.exists():
            return None
        result = bounded_json(result_path)
        if result.get("request_sha256") != ticket["request_sha256"] or result.get("id") != ticket["id"]:
            raise ValueError("Host receipt identity mismatch")
        return result

    ready = result_if_ready()
    if ready is not None:
        return ready
    data = trigger_data(ticket)
    with trigger.open("rb", buffering=0) as stream:
        committed = read_trigger(stream)
    if committed is not None and committed != data:
        raise ValueError("Another or altered trigger is present")
    if committed is None and time.time() >= ticket["trigger_expires_at"]:
        raise ValueError("Dispatch ticket expired; collect the private receipt without re-arming")
    if committed is None:
        publish_trigger(trigger, data)
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        ready = result_if_ready()
        if ready is not None:
            return ready
        time.sleep(0.1)
    return {"id": ticket["id"], "status": "pending", "accepted": False,
            "ticket_path": str(ticket_path), "request_sha256": ticket["request_sha256"],
            "message": "Client wait ended; host work was not stopped. Reuse this ticket to collect its result."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    host = sub.add_parser("serve", help="Authenticated host: arm exactly one approved request")
    host.add_argument("job")
    host.add_argument("--state-dir", required=True)
    host.add_argument("--bridge-dir", required=True)
    host.add_argument("--codex", default="codex")
    host.add_argument("--trigger-timeout-seconds", required=True, type=int)
    client = sub.add_parser("request", help="Sandbox client: trigger and await the host-approved request")
    client.add_argument("ticket")
    client.add_argument("--wait-seconds", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        if args.action == "serve":
            result = serve(runner.read_json(args.job),
                           runner.absolute_directory(args.state_dir, "state-dir", existing=False),
                           runner.absolute_directory(args.bridge_dir, "bridge-dir", existing=False),
                           runner.executable(args.codex), args.trigger_timeout_seconds,
                           on_ready=lambda value: print(json.dumps(value), flush=True))
        else:
            result = request(args.ticket, args.wait_seconds)
        print(json.dumps(result, ensure_ascii=True, allow_nan=False), flush=True)
        return 0 if result["status"] == "ready_for_review" else 1
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "error": f"{type(exc).__name__}: {exc}"}))
        return 1


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, runner.interrupt_handler)
    sys.exit(main())
