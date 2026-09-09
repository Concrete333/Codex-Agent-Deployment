# Claude CLI workers

Use this route only when Claude delegation and its subscription use are authorized. Choose a suitable configuration using [model-selection.md](model-selection.md); do not load another deployment skill.

## Before dispatch

- Requires Python 3.10+ and logged-in Claude Code 2.1.108+ for the five-minute cache override. On Windows use native `claude.exe`, not a shell shim. Version/authentication checks are read-only; `--dry-run` performs no Claude calls and does not verify installed-version compatibility.
- Workers use five-minute caching (`FORCE_PROMPT_CACHING_5M=1`) and disabled skill discovery (`--disable-slash-commands`). The default Claude coding prompt stays intact. These overrides apply only to the child process, not your interactive settings. Do not resume merely to keep a cache warm.
- Supply a bounded assignment and relevant evidence paths/ranges. Workers need applicable project instructions, not the coordinator's routing policy, CLI manual, wrapper source or benchmark rationale unless those are the assigned subject. Reuse valid evidence and request a concise handoff, normally within 200 words, preserving exact failures and decision-critical details.
- Inspect the target checkout and inherited Claude instructions, memory, hooks, plugins and configuration before setting `trusted_context: true`. Subscription mode is not bare mode. The wrapper disables settings sources and configured MCP servers, but is not a sandbox or a guarantee that no inherited behavior executes. Do not run in untrusted repositories.
- The wrapper removes alternate provider/API credentials from the child environment and checks for local Claude.ai login. Do not enable paid overflow, change credentials, or retry through another billing route. Confirm account-side extra-usage settings separately: this wrapper cannot enforce a subscription-only spending ceiling at the server.
- Set ownership and acceptance in the prompt. Review/explore expose only Read, Glob and Grep. Edit adds Edit and Write; `allow_shell: true` additionally permits unrestricted Bash and must be explicitly authorized. These tool sets do not enforce a directory sandbox. Do not grant shell access just to inspect a diff; supply it as evidence instead.

## Invoke

Create a UTF-8 JSON request in the task's appropriate scratch location. Run the script from the installed skill directory, or use its absolute path:

```powershell
python scripts/claude_worker.py C:/path/to/task/claude-request.json --dry-run
python scripts/claude_worker.py C:/path/to/task/claude-request.json
```

Request example (replace the model with an account-supported, explicitly selected model ID):

```json
{
  "max_concurrent": 1,
  "jobs": [{
    "id": "correctness-review",
    "model": "YOUR_SELECTED_CLAUDE_MODEL_ID",
    "effort": "high",
    "profile": "review",
    "cwd": "C:/path/to/project",
    "trusted_context": true,
    "timeout_seconds": 1800,
    "prompt": "Review the assigned diff against the requirements supplied here. Do not edit. Return findings with file locations, triggers, impact and evidence; identify checks you could not run. [Include requirements, diff/evidence paths, scope and acceptance checks.]"
  }]
}
```

Profiles: `review`, `explore`, `edit`. Efforts: `low`, `medium`, `high`, `xhigh`, `max`; availability depends on the selected model and installed CLI. Optional job fields: `session_id`, `allow_shell` (edit only), `max_budget_usd` (positive API-cost estimate cap, not an allowance meter). Models and efforts have no defaults or fallback. The CLI rejecting a configuration is a blocker, not permission to substitute one.

Add jobs and explicitly raise `max_concurrent` (1–4) for independent work. Concurrent jobs involving edits require non-overlapping checkouts; separately ensure no shared mutable resources or unsettled interfaces. Do not concurrently resume the same session. A batch limit is local to that invocation, not machine-wide. Do not launch overlapping batches to bypass it. Sequential jobs do not automatically receive previous results; inspect and prepare a continuation when it depends on earlier work.

Use the shell runtime's persistent execution/session mechanism to await a long-running batch. Avoid repeated status calls or launching replacements. The wrapper waits for its workers and emits one JSON batch result, not periodic model wakeups. Choose an actual work budget: the default 30-minute timeout terminates the worker, unlike a harmless coordinator wait timeout. Do not terminate the wrapper while workers are active; if externally interrupted, check for remaining processes before transferring ownership.

## Interpret and continue

- `returned` means the CLI reported success, **not** accepted work. Inspect the result and artifacts; a worker can report a blocker in its prose even after a successful CLI exit.
- `partial` includes timeouts and recognized turn/cost limits. `blocked` includes authentication, permission denials, process errors and malformed output. No automatic retry.
- Stdout returns compact receipts: requested model/effort, reported model identities, session ID, exit status, duration, token totals, cost estimate and up to 4,000 characters of result. `result_truncated` marks a preview, not a full answer. When `details_require_read` is true, inspect the full receipt before accepting work or retrying; do not infer omitted failures from the preview.
- Each `receipt_path` points to complete result, CLI stdout/stderr and detailed telemetry, saved before the compact response. Files live in a unique `claude-worker-receipts-*` system-temp folder by default. Use `--receipt-dir C:/path/to/task-scratch` to retain them under an existing absolute directory. Keep needed evidence before temporary-file cleanup; never commit private receipts to the skill repository. If saving fails, the wrapper returns the full receipt instead of discarding evidence.
- `cache_ttl_check` is `confirmed_5m` only when five-minute writes are observed, `mismatch` when one-hour writes occur, otherwise `unknown` (including cache-hit-only runs). Inspect a mismatch before further dispatch. Compare reported models with the request; aliases may resolve to full IDs, and usage can include internal helper calls. An extra reported identity alone does not prove worker fallback; investigate worker configuration when material. Effective effort is not claimed verified. Missing telemetry is unknown, not zero usage.
- Resume with the returned `session_id`, the same checkout and explicit model/effort/profile. Preserve scope and tell the worker what changed. Do not assume a new permission profile erases session history.
- After timeout, verify termination and remaining writing commands before reassigning files, even if the tree-kill command succeeded. Preserve partial edits. A failed cleanup keeps ownership unresolved.
- Results and stderr can contain private project data. Do not publish raw receipts or commit them to the skill repository.

CLI capability reference: [Anthropic programmatic usage](https://code.claude.com/docs/en/headless). Verify current account billing when setting up the route: [subscription usage notice](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan).
