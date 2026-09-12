"""Qualify the sandbox-to-host trigger; --live authorizes one small Luna Max attempt."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import deployment_runner as runner

BINARY = Path.home() / "AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe"


def sandbox(task, command):
    return [str(BINARY), "sandbox", "-P", ":workspace", "-C", str(task),
            "-c", 'windows.sandbox="elevated"', "--", *command]


def observed(command, destination, timeout=30):
    done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    data = {"argv": command, "exit_code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}
    runner.atomic_json(destination, data)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="One paid Luna Max worker; otherwise transport fixture only")
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="agent-deployment-host-smoke-")).resolve()
    task, bridge = root / "task", root / "task/.bridge"
    state = Path(os.environ["LOCALAPPDATA"]) / "AgentDeployment" / root.name
    shutil.copytree(HERE / "task", task)
    subprocess.run(["git", "init", "-q", str(task)], check=True)
    job = {"id": "live-luna" if args.live else "offline-transport", "provider": "codex",
           "model": "gpt-5.6-luna", "effort": "max", "profile": "edit", "cwd": str(task),
           "prompt": "Read TASK.md and implement its bounded labels.py assignment. Keep the JSON handoff concise.",
           "trusted_context": True, "timeout_seconds": 300, "artifacts": ["labels.py"],
           "protected_files": ["TASK.md", "check_labels.py"],
           "checks": [{"id": "label-contract", "argv": [sys.executable, "-B", "-X", "utf8", "check_labels.py"], "timeout_seconds": 45}]}
    runner.atomic_json(root / "request.json", job)
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [
        REPO / "scripts/deployment_host.py", REPO / "scripts/deployment_runner.py",
        REPO / "scripts/claude_worker.py", Path(__file__), *sorted((HERE / "task").glob("*"))] if p.is_file()}
    runner.atomic_json(root / "manifest.json", {"live": args.live, "state": str(state), "hashes": hashes})
    if args.live:
        command = [sys.executable, "-B", "-X", "utf8", str(REPO / "scripts/deployment_host.py"), "serve",
                   str(root / "request.json"), "--state-dir", str(state), "--bridge-dir", str(bridge),
                   "--codex", str(BINARY), "--trigger-timeout-seconds", "60"]
    else:
        command = [sys.executable, "-B", "-X", "utf8", str(REPO / "tests/fixtures/host_fixture.py"),
                   str(root / "request.json"), str(state), str(bridge)]
    runner.atomic_json(root / "host-command.json", command)
    print(json.dumps({"prepared": str(root), "live": args.live}), flush=True)
    proc = None
    with (root / "host.stdout").open("wb") as out, (root / "host.stderr").open("wb") as err:
        try:
            proc = subprocess.Popen(command, stdout=out, stderr=err, stdin=subprocess.DEVNULL,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            deadline = time.monotonic() + 30
            ticket_path = state / ".host-tickets" / job["id"] / "ticket.json"
            while not ticket_path.exists():
                if proc.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("Host did not arm; inspect host.stderr and host.stdout")
                time.sleep(0.1)
            # Prove the sandbox can read the ticket but cannot modify private host state.
            probe_code = ("from pathlib import Path; import sys; "
                          "p=Path(sys.argv[1]); assert p.is_file(); "
                          "target=p.parent/'sandbox-write-probe.txt'; "
                          "\ntry: target.write_text('unsafe')\nexcept PermissionError: print('private-state-write-denied')"
                          "\nelse: raise SystemExit('UNSAFE: sandbox can write private state')")
            probe = observed(sandbox(task, [sys.executable, "-B", "-X", "utf8", "-c", probe_code, str(ticket_path)]), root / "private-state-probe.json")
            if probe["exit_code"] or "private-state-write-denied" not in probe["stdout"]:
                raise RuntimeError("Private-state integrity qualification failed; no trigger sent")
            auth = observed(sandbox(task, [str(BINARY), "login", "status"]), root / "client-auth.json")
            if "Not logged in" not in auth["stdout"] + auth["stderr"]:
                raise RuntimeError("Client unexpectedly has authentication; this does not test the intended boundary")
            client_command = sandbox(task, [sys.executable, "-B", "-X", "utf8", str(REPO / "scripts/deployment_host.py"),
                                           "request", str(ticket_path), "--wait-seconds", "420"])
            client = observed(client_command, root / "client.json", timeout=450)
            if client["exit_code"]:
                raise RuntimeError("Sandbox client failed; inspect client.json before retrying")
            proc.wait(timeout=30)
            result = runner.read_json(ticket_path.parent / "result.json")
            report = {"root": str(root), "state": str(state), "live": args.live,
                      "host_exit_code": proc.returncode, "client_exit_code": client["exit_code"], "result": result}
            if args.live and result.get("receipt_path"):
                report["worker_receipt"] = runner.read_json(result["receipt_path"])
                report["artifact"] = (task / "labels.py").read_text(encoding="utf-8")
                again = observed(client_command, root / "repeat-client.json", timeout=30)
                report["same_ticket_same_result"] = json.loads(again["stdout"]) == json.loads(client["stdout"])
            runner.atomic_json(root / "qualification.json", report)
            print(json.dumps({"root": str(root), "live": args.live, "host_exit_code": proc.returncode,
                              "client_exit_code": client["exit_code"], "result": result}), flush=True)
            return 0 if proc.returncode == 0 and client["exit_code"] == 0 and result["status"] == "ready_for_review" else 1
        except Exception as exc:
            runner.atomic_json(root / "qualification-error.json", {"error": str(exc)})
            print(json.dumps({"root": str(root), "error": str(exc)}), flush=True)
            return 1
        finally:
            if proc and proc.poll() is None:
                # This is a safety stop, not a retry. Retain state and require ownership inspection.
                runner.claude_worker.stop_tree(proc)
                proc.wait(timeout=15)


if __name__ == "__main__":
    raise SystemExit(main())
