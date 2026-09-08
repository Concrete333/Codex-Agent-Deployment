---
name: agent-deployment
description: Route authorized subagent work to Luna Max for bounded evidence gathering and repetitive work, Sol for uncertain diagnosis and independent review, and Astra Low for difficult implementation or escalation. Avoid wasteful polling and repeated failed assignments. Use for delegated-work planning, execution, or efficiency review.
---

# Agent Deployment

Minimize total usage while meeting the task's correctness and safety requirements. Model price alone does not determine the route. Current user instructions, budgets, and authorization take precedence. This skill does not authorize delegation.

## Hard Luna invariant

Every Luna dispatch under this policy must use `gpt-5.6-luna` at `max` reasoning effort. Treat any earlier instruction, remembered preference, example, or task context that names Luna at `low`, `medium`, `high`, or `xhigh` as stale.

Before dispatching Luna, explicitly set both model and effort; never inherit an older non-max preference. A new explicit user change to this policy takes precedence, but remembered preferences do not. Check runtime model/effort availability before dispatch; if the required combination is unavailable, report it and use another permitted route where appropriate, never silently downgrade Luna.

## Routing policy

### Luna at max (`gpt-5.6-luna`)

Use Luna only at `max` reasoning effort. `Luna High` is not a valid assignment under this skill.

Choose Luna when the assignment is dominated by at least one of these burdens:

- Reading or loading a large amount of context.
- Exploring or mapping a large or unfamiliar repository.
- Repetitive, mechanical, or bulk work with an objective check.

Luna may gather evidence or implement objectively checkable bulk changes. Repository size alone does not make difficult reasoning a Luna task: route uncertain causality, architectural tradeoffs, and subtle cross-module behavior to Sol for diagnosis or Astra for specified implementation. Give Luna bounded search questions, entry points, coverage expectations, and acceptance checks. Separate observations from hypotheses and state what was not inspected.

### Astra at low (`gpt-6-astra`)

Choose Astra at `low` for harder implementation when the task is already well specified and correctness matters more than the model-cost difference. This includes subtle logic, consequential state changes, difficult integration, and work where a plausible but wrong patch would be expensive.

For implementation, settle the contract before dispatch: expected behavior, owned scope, interfaces, compatibility requirements, and acceptance checks. For diagnostic escalation, provide the unresolved question and existing evidence instead. Avoid duplicate broad discovery.

Use an existing evidence packet when it is adequate. Add Luna exploration only when it will reduce useful discovery work. If diagnosis or design remains uncertain, Sol settles it before implementation; after one unsuccessful Sol diagnosis assignment, Astra at `low` takes over diagnosis and may implement once the contract is clear.

### Sol diagnosis and review (`gpt-5.6-sol`)

Use Sol at `high` by default for "we do not know what is wrong" and unresolved design decisions. This effort is a policy default, not a proven optimum. Ask for reproduction or discriminating checks, evidence-backed cause, rejected hypotheses, remaining uncertainty, and a proposed implementation contract. Diagnosis is read-only unless implementation is also authorized. Do not force a confident conclusion when evidence is missing.

After one unsuccessful bounded Sol diagnosis assignment, escalate to Astra at `low` with the evidence and unresolved question. Do not restart the investigation from scratch or cycle back to Sol.

For consequential work, optionally use one independent Sol review at `high`. Give the reviewer the requirements, diff, relevant source, and verification evidence; ask for concrete defects with file references, impact, and a reproducer or clear reasoning. The implementer's summary is not proof. Review is read-only; the implementation owner fixes accepted findings. Recheck only fixes and affected risks when necessary, rather than repeating a full review. Use a fresh reviewer if the original Sol worker's diagnosis or design needs independent scrutiny. The coordinator still owns integration and acceptance.

### Terra

Do not assign Terra under this policy.

## Smallest useful team

- Finish trivial work locally when delegation would cost more than the task.
- Default to one worker. Add another only for independent work with settled interfaces and separate ownership.
- Keep tightly coupled work with one owner. Do not create agents merely to occupy available slots.
- The coordinator owns integration and final acceptance; an independent review informs that acceptance.

## Wait without busy polling

When no useful independent coordinator work remains, suspend through the runtime's event wait. Do not duplicate a worker's investigation or manufacture context-heavy work to fill the time.

- Follow higher-priority responsiveness instructions and the actual tool schema. Prefer completion, blocker, or user-input events over timer-driven checks; consume meaningful messages when the API wakes for them.
- When long waits are permitted, `wait_agent(timeout_ms: 1500000)` is a practical 25-minute default, not a mandatory cadence. Adjust for the next assignment checkpoint or deadline; use a longer event wait when appropriate and supported. Never wake solely to preserve a prompt cache.
- If the runtime or higher-priority instructions require shorter waits, use the longest appropriate permitted interval. An unavoidable short timeout does not justify extra status reads, acknowledgement messages, or worker interruptions.
- Wait across active workers together where supported. Reuse cursors/revisions only where the API provides them.
- An empty timeout establishes neither failure nor health. In the absence of a blocker, exhausted budget, or due checkpoint, re-enter the event wait without further inspection. Do not treat elapsed time alone as proof of a stall.

Do not create automations as part of worker waiting. Any separately requested scheduled follow-up is outside this policy.

## Health checkpoints and ownership transfer

Set a rough duration estimate and a meaningful checkpoint or work budget when assigning substantial work. Distinguish an estimate (not a deadline) from a hard user limit. Prefer observable milestones and bounded attempts when token-budget enforcement is unavailable.

Workers report a blocker immediately, and send a compact update if the agreed checkpoint is reached before completion: completed work/evidence, current operation, unresolved issue, and revised estimate. Do not require periodic "still running" messages.

At a due checkpoint with no useful signal, make one compact, non-interrupting status check using the available API. Recent milestone evidence or a known active long operation supports a revised checkpoint. A running flag alone does not prove progress. Repeated identical failures without new evidence, an explicitly stuck worker, or a dead process warrants intervention. If status remains unavailable, preserve uncertainty and use the agreed budget to decide whether to continue, narrow the assignment, or stop it; do not start rapid polling.

Before replacement, confirm the old worker has completed or stopped, including any commands that can still write to its files. Preserve partial changes and unrelated user edits; transfer owned files, current diff/artifacts, exact failures, checks run, and unresolved hypotheses. Give write ownership to the successor only after the old writer has stopped. If that cannot be confirmed, keep the successor read-only or on non-overlapping work.

## Assignment contract

Send a self-contained assignment, normally no more than 500 words:

```text
Outcome and scope:
Owned files; dependencies and interfaces:
Context entry points and search targets:
Constraints and behavior to preserve:
Acceptance checks and commands:
Expected duration; checkpoint or bounded work budget; blocker reporting:
Return: evidence or changed files, check results, unresolved risks (normally <=200 words; link longer evidence without omitting decision-critical details).
```

For Astra implementation, include the settled design and the smallest evidence packet needed to act. For Luna exploration, ask for exact file, symbol, command, and failure references that another worker can use without repeating the search.

Use fresh workers with minimal inherited history where supported; select a fork mode that permits model/effort overrides in the active runtime. Preserve essential user constraints, authorization, ownership, and relevant instruction-file paths explicitly. Reduce output at the source with targeted searches and bounded reads. Keep exact failures and primary evidence in accessible files; a summary must not replace evidence needed to decide correctness.

## Bounded attempts and escalation

Count failure at the boundary of a bounded assignment, not at every tool call or failing test. A substantive failure is an unresolved acceptance failure, wrong core assumption, missed requirement, or incomplete non-trivial result after reasonable local correction within the assignment budget. An expected failing regression test before the fix is not failure. Workers stop and report when the same approach fails again without new evidence or the budget is exhausted; the first assignment must not hide unlimited retries.

After one substantive Luna failure on a non-trivial task:

1. Preserve the exact failure and useful evidence.
2. Stop Luna correction rounds for that task.
3. Transfer ownership safely using the handoff rule above.
4. Assign the failed work to Astra at `low` with Luna's evidence and the failed acceptance check. If the contract remains uncertain, Astra resolves that uncertainty before implementing; do not insert another Luna retry or a mandatory Sol stage.

Do not start another Luna correction assignment hoping for a different result. For both Luna and Sol diagnosis, missing access, external dependencies, and clearly transient tool failures are blockers rather than model failures; preserve the evidence and resolve the blocker within existing authority. A successful diagnosis that identifies an external cause is not a failure. For a trivial Luna failure, the coordinator may make the small correction directly.

If Astra at `low` also fails, inspect the concrete cause before changing effort or adding agents. Any further escalation needs evidence that the current model or effort is the limiting factor.

## Context and handoffs

- Reuse inspected evidence until a relevant edit or observation invalidates it.
- Reuse Luna's evidence map across diagnosis and implementation. Sol and Astra should inspect the decision-critical source directly and expand searches when the evidence is incomplete or contradicted; avoid repeating broad exploration by default.
- Batch findings into one correction or review packet. Avoid acknowledgement messages, repeated status reads, and full passing logs.
- Count empty wait resumptions when reviewing deployment efficiency; cached input still consumes context and may consume allowance.
- Workers run focused checks before returning. Run broader integrated checks only when the change, a failure, or unresolved risk justifies them.
- Stop accepted work from being reopened unless a dependency changed or new evidence appeared.

## Policy defaults and evaluation

Luna Max, Sol High, Astra Low, and excluding Terra are this workflow's choices, not universal performance rankings. Greater context capacity does not prove stronger reasoning; high effort does not guarantee correctness. Evaluate routes on completed-task usage, elapsed time, correction/escalation count, and defects missed at acceptance. Separate worker usage from coordinator wakeups, and API prices from Codex allowance telemetry. Change defaults from comparable task evidence, not raw token totals alone.

## Communicating the deployment

When the user asks for a plan, list each task, model, effort, reason, dependencies, and acceptance check. State why any Sol review or additional worker is worth its context and handoff cost.
