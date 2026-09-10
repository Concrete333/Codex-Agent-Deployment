---
name: agent-deployment
description: Guide Codex orchestrators in choosing Luna, Terra, Sol or Opus 5 workers, assigning bounded work and verifying results. Use when planning, executing or auditing authorized delegation.
---

# Agent Deployment

Minimize total cost to an accepted result: coordinator context and decisions, workers, checks and corrections. Meet the required correctness standard; speed is not the goal. This skill does not authorize delegation, additional spending, billing changes or paid overflow.

## First decide: local or delegated

Keep small or tightly coupled work local. Before reading the model guide or spawning, identify **a bounded workload the coordinator will stop doing** and **how to check its result without solving it again**. If preparation, duplicated understanding and likely repair erase the benefit, stay local. Prefer commands and scripts for deterministic work.

Useful boundaries include an evidence search that keeps bulky source material out of the coordinator's context, or a settled component delivered with its tests and corrections. Separate files, a large project or an inexpensive worker are not sufficient reasons to delegate. Do not write a full solution merely to make a cheap worker usable.

The coordinator owns consequential behavior, interfaces and acceptance. Resolve those decisions before implementation; delegate bounded evidence gathering if needed. Prefer one owner for tightly coupled implementation and regression tests through corrections. Separate test design or review only when its independent coverage or reasoning addresses a named risk.

Judge the remaining uncertainty, not the artifact name. Following a known test pattern with settled expected results can be mechanical; discovering regression cases for unfamiliar behavior is reasoning work.

If staying local, skip the remaining dispatch guidance and model catalogue.

## Choose the worker

Workers may use only **GPT-5.6 Luna, GPT-5.6 Terra, GPT-5.6 Sol or Claude Opus 5**. No Astra or Fable workers, including reviewers, forks and nested delegates. Keep open-ended diagnosis, architecture, difficult coupled reasoning and consequential final judgment with the current orchestrator. Do not move that work to an expensive allowed worker to bypass this boundary.

Keep the orchestrator's model and effort. If its capability or access is insufficient, report the limitation and request direction.

Read the cost check and relevant candidates in [model-selection.md](references/model-selection.md). Choose for the hardest requirement left in the bounded assignment. State the model, effort, displaced work and acceptance check briefly; no separate planning document is needed. For authorized Opus 5 use, also read [claude-cli.md](references/claude-cli.md) and use the wrapper.

Reuse inspected guidance. Do not load or search `docs/` during ordinary deployment; maintenance and audits may consult it. Workers receive applicable project instructions and their assignment, not this policy, model guide or benchmark material.

## Assign ownership and done

Start with one worker. Add workers only for independently useful scopes with settled interfaces and separate write ownership, including shared mutable resources. Workers may redelegate only with assigned permission, supported controls and the same model restrictions.

Set model and effort explicitly, use minimal inherited history, and check effective settings when exposed. Full-history forks can inherit the coordinator's configuration. An unavailable control or mismatched setting is a blocker, not permission to substitute.

For isolated checkouts, specify the starting revision and needed uncommitted changes. Give a short, self-contained assignment:

```text
Outcome, scope and non-goals:
Owned files/resources, permissions, dependencies and interfaces:
Evidence paths/ranges, search boundaries and relevant instructions:
Settled decisions and rationale; local choices left to the worker:
Required behavior, important failure cases and acceptance checks:
Work budget or observable checkpoint; report blockers promptly:
Return complete | partial | blocked, artifacts, checks/results and unresolved risks.
```

Challenge consequential assumptions and whether the checks would detect their failure before dispatch. Leave local implementation choices with the owner. Diagnosis and review stay read-only unless specific reproduction or scratch edits are assigned.

Do not investigate or implement the active worker's assignment in parallel. Work on independent coordinator responsibilities or wait. Keep handoffs concise, linking artifacts and preserving exact failures, constraints and decision-critical evidence. Retrieval needs source locations and coverage gaps; absence claims need search scope, and completeness claims need coverage or count reconciliation.

## Verify, then finish

The coordinator accepts the result at its existing effort. Inspect the diff, relevant source and evidence against the agreed behavior—not just the worker's completion summary. Use a requirement-derived counterexample or independent expected result where shared assumptions could hide failure. Verify affected interactions after integration and tie results to the tested state.

The owner runs focused checks and handles corrections. Reuse valid evidence for unchanged work; inspect underlying sources when summaries are insufficient or contradicted. Recheck changed risks, with broader tests when acceptance or interactions require them, rather than restarting the investigation.

Add a reviewer only for a named risk or useful independence. Findings need a location, trigger, impact and evidence; prioritize credible correctness, security and data-integrity defects over speculative hardening or finding counts.

Finish when required checks and inspection support acceptance. Reopen for new evidence, changed dependencies or required review—not to expand optional hardening. Only the coordinator may revise acceptance criteria within user authority; never weaken assertions to pass or fit a budget. A successful process exit is not acceptance.

## Continue or recover

Local tool errors and expected failing regression tests are not assignment failure. Allow corrections within budget; do not repeat an approach without new evidence.

- **Blocked:** Resolve missing decisions, access or environment within authority; changing models is not the default fix.
- **Partial:** A checkpoint, turn limit or work budget ended. Preserve progress; continue only with a credible remaining plan within user limits.
- **Substantive failure:** Core behavior remains wrong after the bounded attempt. Repair missing evidence or specification; return reasoning beyond the worker's scope to the orchestrator.

After one substantive non-trivial Luna failure, do not repeat the assignment on Luna. Choose local completion or a revised bounded assignment to another allowed worker deliberately, not an automatic model/effort ladder. A review finding defects has succeeded.

Reuse suitable owners and valid findings. Before transferring writes, confirm the previous worker and writing commands have stopped; pass the diff, failures and open questions. If termination is uncertain, keep successors read-only or non-overlapping. Preserve unrelated edits.

## Wait without busy polling

Before delegation likely to leave the coordinator idle, confirm a supported completion wait within host responsiveness rules. Reuse that finding until runtime/configuration changes. If unavailable, stay local or report the limitation; timeout configuration alone does not establish tool availability.

Use event-driven completion waits and supported cursors, choosing the longest suitable wait permitted by responsiveness rules, tool limits, deadlines and checkpoints. Do not substitute repeated sleeps, status checks, wrapper polling or scheduled automations, or wake merely to preserve a cache.

An empty timeout proves neither failure nor health. Resume waiting without extra status reads or replacing workers unless a due checkpoint, blocker or exhausted budget requires action. At a checkpoint, use one compact non-interrupting milestone check. Distinguish a wait timeout from a work timeout that terminates the worker.

When measuring cost, count parent and child input/cache use, output, preparation, reviews, failed attempts and integration. Worker savings are not team savings; API estimates are not subscription allowance consumption.
