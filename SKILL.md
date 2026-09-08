---
name: agent-deployment
description: Route authorized subagent work to Luna Max for evidence and repetitive edits, Astra Light for implementation and correctness review, or Sol High for diagnosis and targeted hardening. Use when planning, executing, or auditing delegated work.
---

# Agent Deployment

Minimize total cost to an accepted result, including coordination, review, and corrections, while meeting correctness requirements. Token counts help identify waste but do not replace cost or quality measures.

This skill does not authorize delegation or expand scope. Higher-priority instructions and new explicit user choices take precedence.

## Dispatch

- Luna uses `gpt-5.6-luna` at `max`.
- Sol defaults to `gpt-5.6-sol` at `high`. Astra Light means `gpt-6-astra` at `low`. Do not assign Terra.
- Set model and effort explicitly through a supported dispatch/fork mode. If unavailable, report the limitation and choose a suitable authorized alternative; never silently downgrade Luna.
- Keep work local when delegation costs more than it saves. Start with one worker; add workers for independent assignments with separate ownership. No mandatory model sequence.
- The coordinator owns routing, integration, escalation, and final acceptance. Workers return results or blockers and may redelegate only with assigned permission.

## Choose the role

### Luna: evidence and repetitive implementation

Use Luna Max for bounded retrieval, extraction, repository mapping, or repetitive edits with objective checks. Require exact file/symbol references, coverage gaps, and observations separated from hypotheses. Delegate exploration only when it reduces downstream work; skip it when adequate evidence exists. Repository size alone does not justify assigning difficult reasoning to Luna.

### Sol: uncertain diagnosis

Use Sol High when the cause or design is unclear. Require reproduction or discriminating checks, an evidence-backed explanation, remaining uncertainty, and an implementation contract. A plausible hypothesis is insufficient.

Diagnosis is read-only except for explicitly assigned scratch/test edits needed for reproduction. General permission to fix a project does not give the diagnostic worker production-write ownership.

### Astra: non-mechanical implementation

Use Astra Light for non-mechanical, well-specified implementation, including ordinary features beyond repetitive edits. Supply expected behavior, interfaces, compatibility constraints, and acceptance checks.

## Review and acceptance

Mechanical edits with strong checks need no mandatory extra reviewer. Prefer Astra Light for separate material-correctness review when justified. An Astra coordinator reviews worker results at its existing effort; do not spawn another Astra to duplicate it. Use a separate reviewer when independence from implementation or design is needed.

Use Sol High for optional edge-case and hardening review of specified release, security, data-integrity, concurrency, compatibility, or coverage risks. A release alone does not require another pass. Raise Sol to Max only for a concrete unresolved reasoning need or explicit user choice.

Reviews are read-only. Inspect requirements, diff, relevant source, and checks rather than trusting the implementer's summary. Findings need locations, triggering conditions, impact, and evidence. Prioritize impact and credible exposure, not finding count; rare security or data-loss cases can be critical. Separate actionable defects from optional hardening and unsupported hypotheses.

Workers run focused acceptance checks. The coordinator integrates results and runs broader checks only when changes or unresolved risks justify them. Route fixes to the implementation owner and recheck affected risks without repeating the full review by default.

## Assignments and evidence

Send a self-contained packet, normally within 500 words:

```text
Role, outcome, and scope:
Owned files; read/write permissions; dependencies and interfaces:
Relevant instructions, evidence paths, and search entry points:
Constraints and behavior to preserve:
Acceptance checks:
Expected duration; checkpoint or work budget; blocker reporting:
Return: results, exact failures/checks, artifacts, and unresolved risks.
```

Use minimal inherited history while preserving user constraints and permissions. Reuse suitable workers for in-scope continuations. Reduce output through targeted searches and bounded reads. Handoffs should normally fit 200 words, linking longer evidence without omitting decision-critical details. Reuse valid evidence; Sol and Astra inspect relevant source and expand searches when evidence is incomplete or contradicted.

## Attempts and escalation

Judge failure at assignment acceptance, not each tool call or failing test. Allow corrections within the agreed budget; an expected failing regression test before a fix is not failure. Stop repeating an unsuccessful approach without new evidence.

- **Accepted:** Checks or evidence support the outcome. Reopen only for new evidence, changed dependencies, or required review.
- **Blocked:** Access, external dependencies, or tool failures prevent progress. Resolve within existing authority; switching models is not the default remedy. Identifying an external root cause can be successful diagnosis.
- **Incomplete at checkpoint:** Return progress and remaining work. Demonstrated progress can justify a revised checkpoint within user limits; hard budgets still apply.
- **Substantive failure:** An acceptance failure, wrong core assumption, or missed requirement remains after the bounded attempt, or no credible path to completion exists.

After one substantive non-trivial Luna failure or substantive Sol diagnosis failure, transfer directly to Astra Light. Trivial Luna corrections can stay local. Preserve partial work and evidence; do not restart discovery or cycle through the failed role. Astra resolves remaining uncertainty before implementing, with authorization and assigned write ownership. A review that finds defects has succeeded.

If Astra Light fails, distinguish evidence, environment, specification, and capability problems before continuing. Do not repeat unchanged attempts or increase effort without a concrete reason.

## Waiting and health

Use runtime event waits when no useful independent coordinator work remains; do not duplicate worker work.

- When supported and permitted by higher-priority responsiveness rules, 25 minutes (`timeout_ms: 1500000`) is a practical default. Adjust to checkpoints, deadlines, and actual tool limits; use the longest suitable permitted wait.
- Wait across active workers together where supported, reusing available cursors/revisions. Handle completion, blocker, and user-input events.
- An empty timeout proves neither failure nor health. Resume waiting unless a blocker, due checkpoint, or exhausted budget requires action. Do not add status reads or interruptions after each timeout, wake to preserve cache, or substitute scheduled automations.

For substantial work, agree on an observable checkpoint or budget. Workers report blockers promptly and checkpoint progress, current operation, and revised estimates when able. Do not require periodic "still running" messages or interrupt blocking tools for updates.

At a due checkpoint without evidence, make one compact, non-interrupting check if supported. Judge progress from milestones and operations, not a running flag. Repeated failures without new evidence, a stuck worker, or a dead process warrants intervention. If progress remains unobservable, use the budget to decide whether to continue, narrow, or stop; avoid rapid polling.

## Transfer ownership

Before a successor edits the same files, confirm the prior worker and writing commands have stopped. Preserve partial work and unrelated user edits. Transfer owned files, current diff/artifacts, exact failures, checks, and open questions. If the old writer cannot be confirmed stopped, keep the successor read-only or on non-overlapping work.

## Evaluate the policy

Compare total accepted-task cost, elapsed time, corrections, and missed defects on like-for-like work. Keep API costs separate from Codex allowance telemetry.

When asked for a deployment plan, state roles, models, efforts, scope, dependencies, and acceptance checks; justify extra workers or review.
