"""Detached command execution and one-shot Codex completion delivery."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


def save(path, data):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def validate_target(binary, thread):
    uuid.UUID(thread)
    path = Path(binary)
    if not path.is_absolute() or not path.is_file():
        raise ValueError("Supply an absolute native Codex executable")
    if os.name == "nt" and path.suffix.lower() != ".exe":
        raise ValueError("Use native codex.exe, not a shell shim")
    result = subprocess.run([str(path), "queue", "--help"], capture_output=True,
                            text=True, timeout=15)
    if result.returncode or "--thread" not in result.stdout or "--message" not in result.stdout:
        raise ValueError("Codex queue is unavailable")
    return str(path)


def notify(binary, thread, receipt):
    receipt = Path(receipt).resolve()
    # Claim before delivery: crash/timeout is uncertain, never automatically retry.
    delivery = receipt.with_name(receipt.stem + ".notification.json")
    try:
        with delivery.open("x", encoding="utf-8") as stream:
            json.dump({"status": "attempting", "thread": thread}, stream)
    except FileExistsError:
        try:
            existing = json.loads(delivery.read_text(encoding="utf-8-sig"))
            if not isinstance(existing, dict) or existing.get("status") not in {
                    "attempting", "queued", "failed", "unknown"}:
                raise ValueError("Invalid delivery claim")
            return existing
        except (OSError, UnicodeError, ValueError) as exc:
            return {"status": "unknown", "thread": thread, "receipt": str(receipt),
                    "error": f"Existing delivery claim is unreadable or incomplete: {exc}; "
                             "do not retry automatically"}
    result = {"thread": thread, "receipt": str(receipt),
              "attempted_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        if not receipt.is_file():
            raise ValueError("Completion receipt is missing")
        state = json.loads(receipt.read_text(encoding="utf-8-sig"))
        heading = ("Background attempt needs intervention; worker termination or ownership is unresolved."
                   if state.get("ownership_check_required") or state.get("termination_unconfirmed")
                   else "Background supervisor reported a result.")
        message = (heading + " Inspect the saved receipt at " + str(receipt)
                   + ". Verify completion and ownership before dependent work. "
                   "A failed or partial attempt is not accepted. Continue only the authorized task; "
                   "after confirmed termination and a verified mechanical fix, a safe rerun within "
                   "existing scope and budget needs no renewed permission. Preserve failure evidence; "
                   "do not duplicate side effects or retry uncertain ownership or delivery.")
        completed = subprocess.run([binary, "queue", "--thread", thread, "--message", message],
                                   capture_output=True, text=True, timeout=30)
        result.update(status="queued" if completed.returncode == 0 else "failed",
                      exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    except subprocess.TimeoutExpired:
        result.update(status="unknown", error="Delivery timed out; do not retry automatically")
    except Exception as exc:
        result.update(status="failed", error=str(exc))
    save(delivery, result)
    return result


def execute(request, folder):
    receipt = folder / "process.json"
    try:
        with (folder / "stdout.log").open("wb") as out, (folder / "stderr.log").open("wb") as err:
            completed = subprocess.run(request["argv"], cwd=request["cwd"],
                                       stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        result = {"status": "exited", "exit_code": completed.returncode,
                  "worker_receipt": request.get("receipt"),
                  "validation": "Process exit is not acceptance; inspect worker receipt and artifacts"}
    except Exception as exc:
        result = {"status": "launch_failed", "error": str(exc)}
    save(receipt, result)
    return notify(request["codex"], request["thread"], receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("check", "notify"):
        p = sub.add_parser(action)
        p.add_argument("--codex", required=True)
        p.add_argument("--thread", required=True)
        if action == "notify":
            p.add_argument("--receipt", required=True)
    p = sub.add_parser("start")
    p.add_argument("--request", required=True)
    p.add_argument("--run-dir", required=True)
    p = sub.add_parser("_run")
    p.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.action == "check":
        validate_target(args.codex, args.thread)
        print(json.dumps({"status": "supported"}))
    elif args.action == "notify":
        result = notify(args.codex, args.thread, args.receipt)
        print(json.dumps(result))
        return 0 if result.get("status") == "queued" else 1
    elif args.action == "_run":
        folder = Path(args.run_dir).resolve()
        result = execute(json.loads((folder / "request.json").read_text(encoding="utf-8-sig")), folder)
        return 0 if result.get("status") == "queued" else 1
    else:
        request = json.loads(Path(args.request).read_text(encoding="utf-8-sig"))
        validate_target(request["codex"], request["thread"])
        argv = request["argv"]
        if (not isinstance(argv, list) or not argv or
                any(not isinstance(x, str) or "\0" in x for x in argv) or
                not Path(argv[0]).is_absolute() or not Path(argv[0]).is_file()):
            raise ValueError("argv must name an absolute executable and string arguments")
        cwd = Path(request["cwd"])
        if not cwd.is_absolute() or not cwd.is_dir():
            raise ValueError("cwd must be an existing absolute directory")
        if os.name == "nt" and Path(argv[0]).suffix.lower() != ".exe":
            raise ValueError("argv must use a native executable")
        folder = Path(args.run_dir)
        if not folder.is_absolute():
            raise ValueError("run-dir must be absolute")
        folder.mkdir(parents=True, exist_ok=False)
        save(folder / "request.json", request)
        flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP |
                 subprocess.CREATE_NO_WINDOW) if os.name == "nt" else 0
        with (folder / "supervisor.log").open("wb") as log:
            proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_run",
                                     "--run-dir", str(folder)], stdin=subprocess.DEVNULL,
                                    stdout=log, stderr=log, creationflags=flags,
                                    start_new_session=os.name != "nt", close_fds=True)
        print(json.dumps({"status": "started", "pid": proc.pid, "run_dir": str(folder),
                          "notification": "armed", "receipt": str(folder / "process.json")}))


if __name__ == "__main__":
    sys.exit(main())
