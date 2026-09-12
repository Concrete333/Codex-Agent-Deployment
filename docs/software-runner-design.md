# Software runner: design and qualification

## Purpose

Move predictable lifecycle work out of paid model turns: dispatch one configured worker, wait for process completion, run already-chosen checks and save a compact receipt. The coordinator still chooses the assignment/model and owns substantive verification, correction decisions and final acceptance.

This is an experimental optional adapter, not a replacement for an efficient native completion wait. The runner has no model-based scheduler, automatic retries, reviewer loop, issue tracker, daemon, dashboard or team topology. It starts one fresh worker per request. One active claim per shared state directory limits concurrency and prevents accidental redispatch; there is no machine-wide ownership service.

## What we took from Symphony

Source inspected at commit [`e0ccc83720a42a600a53b61c5f8d3e518bebe1db`](https://github.com/openai/symphony/tree/e0ccc83720a42a600a53b61c5f8d3e518bebe1db). This implementation is original; it does not vendor Symphony code or launch Symphony.

| Source | Applied lesson |
| --- | --- |
| [Orchestrator](https://github.com/openai/symphony/blob/e0ccc83720a42a600a53b61c5f8d3e518bebe1db/elixir/lib/symphony_elixir/orchestrator.ex) | Software tracks claims and completion. Model turns need not own routine scheduling. Our single-slot claim deliberately omits its issue polling and retry machinery. |
| [Agent runner](https://github.com/openai/symphony/blob/e0ccc83720a42a600a53b61c5f8d3e518bebe1db/elixir/lib/symphony_elixir/agent_runner.ex) | Separate worker execution from orchestration state and preserve results. We omit automatic continuation turns and tracker-driven follow-up. |
| [Specification](https://github.com/openai/symphony/blob/e0ccc83720a42a600a53b61c5f8d3e518bebe1db/SPEC.md) | Make lifecycle, workspace and trust boundaries explicit. Process completion is distinct from the business outcome. |

The adapters use [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) and [Claude programmatic mode](https://code.claude.com/docs/en/headless). Codex returns JSONL events and a schema-constrained last message; Claude returns JSON with `structured_output`. The existing Claude wrapper supplies its launch, authentication, environment and cleanup helpers.

## Acceptance and accounting boundaries

The software can establish that a process returned, a structured handoff was received, declared files had particular hashes and specific commands exited with particular codes. It cannot establish that the requirement was interpreted correctly, the tests were sufficient or the worker's risk assessment was sound. `ready_for_review` always carries `accepted: false`.

Prescribed checker/contract files can be fingerprinted before work and compared before/after checks. Artifact fingerprints tie observed checks to listed file contents. Neither feature protects undeclared files or replaces ownership and substantive verification. The runner is not itself a security sandbox. Codex checks now run under the worker's sandbox profile; Claude checks execute directly. Claude profiles and Codex sandboxes are separate provider controls.

Timeouts and interruptions preserve logs and retain ownership for explicit recovery even when tree termination reports success. A hard process crash leaves the claim intact. No stale PID lock is automatically stolen. Recorded-PID checks cannot prove all detached descendants have stopped; recovery requires inspection. Multiple state directories or unrelated processes can bypass the cooperative claim.

Prompts go through stdin. Full evidence is saved once; terminal output contains paths and small factual summaries. Requested settings and reported telemetry remain distinct. Codex usage does not consistently expose effective effort or a dollar cost, so these are not invented. Claude costs are client-side API-equivalent estimates, not a subscription allowance meter. Account-side overflow and worker/command activity outside the declared contract are not bounded by an allowance cap here.

## Qualification on 2026-09-11

The offline suite launches deterministic Python fixtures, **not model CLIs**, through the real subprocess/log/check lifecycle. It covers success, partial/blocker reports, malformed output, CLI failure, missing/multiple completion events, permission denials, cost-limit returns, timeouts, preserved partial logs, claim retention, duplicate requests, changed request IDs, protected-checker changes, artifact changes during checks, compact output with full evidence retention, authentication guards and model/effort restrictions. Existing Claude wrapper regression tests run alongside it.

```powershell
python -B -X utf8 -m unittest discover -s tests -q
```

All 57 offline tests passed on Windows with Python 3.13. Read-only version/authentication checks passed for Codex 0.153.4 and Claude 2.1.266. Both CLIs accepted the generated argument lists with `--help`, without dispatching a worker. Help parsing does not validate every runtime configuration value. This is not an end-to-end paid-worker qualification: host wakeups, real provider output, native sandbox behavior and cost through acceptance still require a controlled live test.

The [subsequent paired-test preflight](benchmarks/runner-preflight-2026-09-11.md) found a launch-context blocker: host-side Codex reports a ChatGPT login, but the same executable reports no login inside the coordinator's Windows sandbox. No paid participant runs were started. A sandboxed coordinator needs a qualified host-side launch mechanism before this nested-CLI comparison can proceed.

The [host-bridge smoke test](benchmarks/host-bridge-smoke/results-2026-09-11.md) subsequently passed with one Luna Max worker. The host authorizes a frozen request; a sandbox client updates a host-owned trigger slot and reads a private receipt. No credentials are copied into the sandbox. The bridge is one-shot, Codex-only and intended for trusted cooperative coordinators, not malicious concurrent checkout writers. Checkpoint hashes are not snapshot isolation. This qualifies the launch boundary, not a cost saving.

## Next comparison

Use the same frozen task, starting files, worker model/effort, assignment and handoff contract, substantive reviewer and acceptance checks in both arms. Record actual prompts and runtime-added context rather than assuming the two launch paths are context-equivalent:

1. Native delegation and completion wait.
2. This runner owns launch, completion bookkeeping and the same final check commands.

Count all coordinator/worker tokens, cache categories, check/review work, repairs and failure costs through acceptance. Score consequential misses and false alarms against held-out cases; do not let fewer checks manufacture savings. Repeat the pair before claiming an advantage. Do not change routing, shorten policy, substitute a reviewer or add retries in the same comparison.

The tool itself does not yet establish savings. Native event waits already avoid one polling failure mode, and a separate CLI worker can add context/startup overhead. Its hypothesis is narrower: software can remove predictable coordinator work without lowering the acceptance standard.

The [first controlled attempt](benchmarks/runner-comparison/results-2026-09-11.md) passed the native arm but failed the software arm before worker launch: its copied temporary client script was unreadable from the sandbox. The canonical repo script remained executable in a no-model probe. This incomplete pair establishes no saving; the next preflight must qualify the exact client path, not just host authentication and private-state integrity.

The [authorized recovery](benchmarks/runner-comparison/results-recovery-2026-09-11.md) repaired the path and a client ancestor-inspection issue. It passed all 244 cases but cost $2.19935520 versus the saved native arm's $1.16000836. The outer shell/tool wait still resumed Astra repeatedly: 41 coordinator responses during worker execution versus one native response. The Python-level wait therefore did not achieve the cost objective in this host. Keep the route experimental and prefer the native event-driven completion path.
