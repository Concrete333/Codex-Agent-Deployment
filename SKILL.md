---
name: agent-deployment
description: Route authorized subagent work to Luna Max for evidence and repetitive work, Sol High for diagnosis and review, or Astra Light for difficult implementation and escalation. Define bounded assignments, safe handoffs, and efficient waits. Use when planning, executing, or auditing delegated work.
---

# Agent Deployment

Minimize total usage while meeting correctness requirements. This skill does not authorize delegation or expand task scope. Higher-priority instructions and new explicit user choices take precedence over these defaults.

## Dispatch rules

- Every Luna dispatch uses `gpt-5.6-luna` at `max`. Earlier non-max preferences are stale; never silently inherit them.
- Sol defaults to `gpt-5.6-sol` at `high`; Astra Light means `gpt-6-astra` at `low` reasoning effort. Do not assign Terra.
- Set model and effort explicitly using the active runtime's supported dispatch/fork mode. If unavailable, report the limitation and choose another authorized route if suitable; never silently downgrade Luna.
- Keep small work local when delegation costs more than it saves. Start with one worker; add workers only for independent assignments with separate ownership. Do not create a mandatory sequence of models.
- The coordinator owns routing, escalation, integration, and acceptance. Workers return results or blockers to it; they do not spawn replacements or redelegate unless their assignment explicitly permits that.

## Choose the role

### Luna: bounded evidence and repetitive implementation

Use Luna Max to search substantial context, map a repository, or make objectively verifiable bulk changes. Give explicit search questions, coverage expectations, and checks. Require exact file/symbol references, observations separated from hypotheses, and coverage gaps.

Repository size alone does not justify assigning difficult reasoning to Luna. Uncertain causality or architectural tradeoffs belong with Sol; difficult specified implementation belongs with Astra. Skip a separate evidence-gathering assignment when adequate evidence already exists.

### Sol: uncertain diagnosis and independent review

Use Sol High when the cause or design is unclear. Require reproduction or discriminating checks, an evidence-backed explanation, remaining uncertainty, and a proposed implementation contract. A plausible hypothesis alone is not a settled diagnosis.

Keep diagnosis within its assigned scope: inspect and run non-destructive checks, but do not ship production changes. If reproduction needs edits, assign a bounded scratch/test scope explicitly. General permission to fix the project does not automatically give the diagnostic worker implementation ownership.

For consequential work, optionally assign an independent Sol review. Supply requirements, diff, relevant source, and check results. Require concrete defects with locations, impact, and supporting evidence; the implementer's summary is not proof. Review is read-only. Use a different worker when independence from the original diagnosis or design matters. Fixes follow the routing and escalation rules; recheck affected risks without automatically repeating the full review.

### Astra: difficult implementation and escalation

Use Astra Light for difficult, well-specified implementation where a plausible but wrong patch would be expensive. Supply expected behavior, scope, interfaces, compatibility constraints, and acceptance checks.

After an unsuccessful Luna assignment or Sol diagnosis, Astra takes over the unresolved work using existing evidence. If the cause or contract remains uncertain, Astra resolves it before implementing. Implementation still requires authorization and assigned write ownership. Do not insert another mandatory discovery stage.

## Assignment and evidence

Send a self-contained packet, normally at most 500 words:

```text
Role, outcome, and scope:
Owned files; read/write permissions; dependencies and interfaces:
Relevant instructions, evidence paths, and search entry points:
Constraints and behavior to preserve:
Acceptance checks:
Expected duration; checkpoint or bounded work budget; blocker reporting:
Return: results, exact failures/checks, artifacts, and unresolved risks.
```

Use minimal inherited history for new workers, preserving essential user constraints and authorization. Reuse a suitable existing worker for an in-scope continuation; do not repeatedly create fresh workers merely to discard context.

Reduce output at the source with targeted searches and bounded reads. Aim for a concise handoff, normally at most 200 words, linking longer evidence without omitting decision-critical details. Sol and Astra inspect relevant source directly and expand searches when evidence is incomplete or contradicted. Reuse valid evidence rather than repeating broad exploration.

## Bounded attempts and escalation

Count failure at assignment acceptance, not at each tool call or failing test. Allow reasonable local correction within the agreed budget; an expected failing regression test before a fix is not failure. Repeating the same unsuccessful approach without new evidence is a reason to stop and report.

Classify the result before routing:

- **Accepted:** Required checks or evidence support the outcome. Do not reopen accepted work without new evidence, changed dependencies, or a required review.
- **Blocked:** Missing access, an external dependency, or a transient tool failure prevents progress. Resolve it within existing authority; switching models is not the default remedy. Identifying an external root cause can be a successful diagnosis.
- **Incomplete at checkpoint:** Return progress and remaining work. An estimate expiring is not model failure; the coordinator can revise the checkpoint for demonstrated progress within user limits. Hard budgets still apply.
- **Substantive failure:** An unresolved acceptance failure, wrong core assumption, or missed requirement remains after the bounded attempt. An incomplete result with no credible path forward also qualifies.

After one substantive non-trivial Luna failure, stop Luna correction assignments and transfer directly to Astra Light. After one substantive Sol diagnosis failure, transfer directly to Astra Light. Preserve exact failures and partial work; do not restart discovery or cycle back through the same failed role. A trivial Luna correction can stay local. A Sol review that finds defects has succeeded; route those defects to the appropriate implementation owner.

If Astra Light also fails, inspect whether the cause is evidence, environment, specification, or model capability before continuing. Do not repeat unchanged attempts or increase effort without a concrete reason.

## Wait and assess health

When no useful independent coordinator work remains, use the runtime's event wait. Do not duplicate worker work to fill the time.

- Follow actual tool limits and higher-priority responsiveness instructions. When permitted, `timeout_ms: 1500000` (25 minutes) is a practical wait default, not a mandatory cadence. Adjust for the next checkpoint or deadline; longer event waits may be appropriate. Never wake solely to preserve cache.
- If shorter waits are required, use the longest appropriate permitted interval. Do not add status reads, acknowledgements, or interruptions after each timeout.
- Wait across active workers together where supported; reuse cursors/revisions only where available. Consume meaningful completion, blocker, and user-input events.
- An empty timeout proves neither failure nor health. Re-enter the wait unless a blocker, due checkpoint, or exhausted budget requires action. Scheduled automations are outside this waiting policy.

For substantial work, set a rough estimate and an observable checkpoint or work budget. Workers report blockers promptly and, when able to send messages, report a reached checkpoint before completion with progress, current operation, and revised estimate. Do not require periodic "still running" messages or interrupt a blocking tool just to send one.

At a due checkpoint without useful evidence, make one compact, non-interrupting check if supported. Use milestones and known operations to revise the checkpoint; a running flag alone is insufficient. Repeated failures without new evidence, an explicitly stuck worker, or a dead process warrants intervention. If progress is unobservable, preserve that uncertainty and decide from the agreed budget whether to continue, narrow, or stop; do not start rapid polling.

## Transfer ownership and verify

Before a replacement writes to the same files, confirm the prior worker and any commands that can still write there have stopped. Preserve partial changes and unrelated user edits. Transfer owned files, current diff/artifacts, exact failures, checks run, and unresolved questions. If the old writer cannot be confirmed stopped, keep the successor read-only or on non-overlapping work.

Workers run focused acceptance checks before returning. The coordinator integrates results and runs broader checks only when changes, failures, or unresolved risks justify them. Independent review informs acceptance; it does not transfer the coordinator's responsibility.

## Evaluate the policy

These model/effort settings are workflow preferences, not universal performance rankings. Compare completed-task usage, elapsed time, corrections, and missed defects. Separate worker usage from coordinator wakeups and API prices from Codex allowance telemetry.

When a deployment plan is requested, state each role, model, effort, scope, dependencies, and acceptance check; explain why extra workers or review are worth their cost.
