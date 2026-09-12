# Software-managed CLI workers

Use `scripts/deployment_runner.py` when an authorized, bounded CLI worker and predefined checks would otherwise need coordinator supervision. Prefer the native subagent route when its completion wait already does the job. The runner does not choose models, retry, review meaning or accept results.

Requires Python 3.10+, Codex CLI 0.153.4+ with ChatGPT login, or the configured Opus 5 route in [claude-cli.md](claude-cli.md). Check inherited project/CLI context before setting `trusted_context`. Windows executables must be native `.exe` files; pass `--codex` or `--claude` if discovery finds a shell shim. Unsupported settings are blockers, not permission to substitute.

## Request and run

Keep request and receipt files in private task storage outside the checkout. Use **one shared state directory for all runner invocations**; it permits one active attempt at a time. Do not switch state directories to bypass ownership.

Example request; replace the paths, assignment, protected files and check with the task's actual contract:

```json
{
  "id": "adapter-1",
  "provider": "codex",
  "model": "gpt-5.6-luna",
  "effort": "max",
  "profile": "edit",
  "cwd": "C:/work/project",
  "trusted_context": true,
  "timeout_seconds": 1200,
  "prompt": "Implement the specified CSV adapter in src/adapter.py. Read SPEC.md and follow the existing adapter interface. Own only src/adapter.py. Preserve quoted fields, embedded newlines and empty values. Report ambiguous requirements. The coordinator owns substantive verification.",
  "artifacts": ["src/adapter.py"],
  "protected_files": ["SPEC.md", "tests/test_adapter_contract.py"],
  "checks": [{
    "id": "adapter-contract",
    "argv": ["C:/Python313/python.exe", "-B", "-m", "pytest", "-q", "tests/test_adapter_contract.py"],
    "timeout_seconds": 120
  }]
}
```

```powershell
python C:/path/to/agent-deployment/scripts/deployment_runner.py run C:/work/requests/adapter-1.json --state-dir C:/work/deployment-state --codex C:/path/to/codex.exe --dry-run
python C:/path/to/agent-deployment/scripts/deployment_runner.py run C:/work/requests/adapter-1.json --state-dir C:/work/deployment-state --codex C:/path/to/codex.exe
```

Dry-run validates and shows arguments; it creates no state, calls no CLI and does not establish compatibility or authentication. A real run performs read-only version/auth checks, then **one worker attempt**, followed by the predefined checks if the worker reports complete. Same ID and unchanged request return the original receipt without spending again. A changed assignment needs a new ID.

Use `provider: "claude"`, `model: "claude-opus-5"` and explicit effort for Opus. Its wrapper controls remain in force: subscription preflight, five-minute caching, disabled skill discovery and tool allowlists. Claude-only fields: `allow_shell` (edit only) and optional `max_budget_usd` (API-cost estimate, not subscription allowance). This runner starts fresh sessions; saved session IDs do not imply automatic resumption.

The timeout terminates work; it is not a polling interval. Total run time also includes authentication, each check's timeout and cleanup. There is no account-wide spending cap.

## Checks, handoff and ownership

- Declare exact artifact files to fingerprint; use an empty list for work with no file deliverable. These hashes cover only listed files, not the entire checkout.
- List existing contract/checker files under `protected_files` to detect changes during execution. Keep other writers out of the checkout. Protected-file checking detects changes at checkpoints; it is not filesystem access control.
- Checks are authorized argument arrays, executed serially in the checkout. Codex checks use the worker's sandbox profile; Claude checks run directly. Use trusted commands. The runner adds no shell but a command can itself execute one. Worker-reported tests remain separate from these observed results.
- The worker owns development checks; the runner owns the listed final checks. Do not rerun them merely to produce another handoff. Artifact hashes must stay unchanged through checks.
- Read the saved handoff and receipt. `ready_for_review` means valid structured output, worker-reported completion, existing declared and handoff-listed files, and no failed declared checks—not accepted work. Empty checks establish no behavioral coverage. Resolve risks and worker-flagged judgment calls against the source.
- `checks_failed`, `partial` and `blocked` require inspection. Raw stdout/stderr, prompt, request, arguments, artifacts' hashes and available usage stay on disk. Missing telemetry is unknown. Effective effort is not independently verified; inspect reported identities/configuration issues before reuse.
- On interruption, timeout or uncertain cleanup, the claim stays held. Inspect recorded processes, descendants, partial edits and shared resources before transferring writes. Once stopped, explicitly release it:

```powershell
python C:/path/to/agent-deployment/scripts/deployment_runner.py release adapter-1 --state-dir C:/work/deployment-state --confirm-stopped
```

Release refuses live recorded PIDs and preserves the original receipt. It does not retry the attempt. Normal CLI exit does not independently prove every detached child stopped; background work is forbidden in the assignment. These cooperative claims cannot police unrelated tools or separate state directories.

For a live coordinator, use a supported host completion wait. The runner blocks in ordinary software and emits one final receipt, but cannot prevent host-driven coordinator wakeups. Do not add a status-poll loop; `status <id>` is for a due checkpoint or recovery. If no appropriate wait exists, keep the native route, stay local or use the external host workflow below.

Keep private receipts out of Git. Worker telemetry excludes coordinator preparation, review and integration; include those when measuring cost through acceptance.

For a predefined host workflow, finish the worker and checks before starting a fresh coordinator acceptance session. Call `review_gate(job, state, binary)` immediately before launch; it revalidates completion, checks and file hashes. Supply the native Codex binary so sandbox-created artifacts can be hashed read-only in the same sandbox if the host cannot read them; keep `deployment_hash.py` beside the runner. A failed gate stops with evidence for inspection, not an automatic retry or paid review. Carry the original contract, settled decisions and bounded handoff into acceptance. Count fresh-session startup and any earlier planning. This needs an external host driver; starting a script from a live coordinator does not suspend that coordinator's outer waiting loop.

## Sandboxed coordinator without CLI authentication

For Codex only, an authenticated host can authorize one frozen request with `scripts/deployment_host.py`. Keep that script, the runner and native executable outside client-writable directories. Keep private state outside the checkout and shared bridge; confirm the client cannot write it before dispatch.

Host:
```powershell
python C:/path/to/scripts/deployment_host.py serve C:/work/requests/adapter-1.json --state-dir C:/work/deployment-state --bridge-dir C:/work/project/.bridge --codex C:/path/to/codex.exe --trigger-timeout-seconds 300
```

Client, using the returned ticket path:
```powershell
python C:/path/to/scripts/deployment_host.py request C:/work/deployment-state/.host-tickets/adapter-1/ticket.json --wait-seconds 1500
```

The client only triggers the approved job and collects its private receipt. It cannot supply commands or change configuration. Credentials remain on the host; the worker and Codex checks remain sandboxed. The host passes a minimal environment, excluding arbitrary host secrets and interpreter hooks.

Use a trusted coordinator and keep other writers out of protected files. This is not immutable checkout isolation or a service for hostile clients. A client wait ending does not cancel host work: collect with the same ticket, never automatically re-arm. An expired, untriggered host starts no worker. Both sides wait in software; do not wrap them in model-driven polling.
