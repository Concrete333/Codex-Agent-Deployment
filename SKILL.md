---
name: agent-deployment
description: Guide Codex orchestrators in choosing GPT or Claude workers, defining bounded assignments, and verifying results with minimal coordination overhead. Use when planning, executing, or auditing authorized delegated work.
---

# Agent Deployment

Minimize total cost to an accepted result, including coordination, context loading, review and corrections. Meet the required correctness standard; speed is not an optimization goal. This skill does not itself authorize delegation, additional spending, billing changes or paid overflow.

## Choose the execution path

1. Define the required outcome and how to check it before choosing a worker. Resolve decision-critical ambiguity; start stronger when consequential uncertainty remains and checks are weak. Prefer commands or scripts for exact searches, counts and deterministic transformations.
2. Assess delegation before loading model-selection guidance. For small, self-contained work already within the coordinator's capability, complete it locally with the required checks; skip model-selection references and assignment packets unless delegation has a concrete benefit. If delegating, start with one worker; add another only for necessary context isolation, independent work or useful independent verification. Hard reasoning alone does not call for a committee.
3. Read [model-selection.md](references/model-selection.md) when choosing a model and effort. It defines acceptance evidence, relative costs, model strengths and effort trade-offs. Choose by the assignment's hardest requirement and explain the choice briefly. These are recommendations, not mandatory roles or an escalation ladder. Honor explicit user choices and account/runtime limits.
4. For Claude workers only, also read [claude-cli.md](references/claude-cli.md) and use the included wrapper. Do not load the other provider's deployment skill.

Do not read or search `docs/` during ordinary deployment. Those files are evidence for audits and skill maintenance, not assignment context. Load only the operational reference needed for the current decision; reuse it until relevant information changes.

Set model and effort explicitly through a supported dispatch mode. A fork or role name does not establish a cheaper configuration. Confirm effective settings when exposed; report unavailable controls or mismatches instead of silently substituting. Keep the coordinator at its existing model and effort unless the user requests a change.

## Ownership and context

The coordinator owns the outcome, cross-cutting decisions and acceptance. Before delegating implementation, settle behavior, interfaces and constraints that would change what counts as correct. If these are unknown, use a bounded investigation to gather evidence or proposals, then resolve the decision before dependent edits. Leave local implementation choices to the owner within those boundaries.

For consequential decisions, challenge the proposed approach: what plausible failure would violate the requirement, and would the planned checks catch it? Tighten the assignment where needed. A short contract is usually enough; do not write a PRD, detailed plan or the implementation itself merely to make a cheap worker usable.

Keep coupled implementation with one owner through fixes and focused checks. Parallel work requires settled interfaces, independent decisions and separate write ownership, including shared mutable resources. Different files alone do not establish independence. Workers may redelegate only with assigned permission and supported runtime controls.

For isolated checkouts, establish the starting revision and required uncommitted changes. Send a self-contained assignment, normally within 500 words:

```text
Outcome, scope and non-goals:
Owned files/resources; read/write permissions; dependencies and interfaces:
Relevant instructions, evidence paths/ranges, search entry points and starting state:
Constraints and settled decisions with rationale; choices left to the worker:
Acceptance checks, expected behavior and important failure cases:
Work budget or observable checkpoint; report blockers promptly:
Return complete | partial | blocked, with artifacts, checks/results and unresolved risks.
```

Use minimal inherited history without dropping constraints or decision-critical evidence. Reuse suitable workers and valid findings for continuations. Do not re-investigate or re-implement active delegated work. Handoffs should normally fit 200 words with links to longer evidence; expand when necessary to preserve exact failures or reasoning-critical details.

Retrieval must return source locations and coverage gaps. Absence claims need a stated search scope; completeness claims need coverage or count reconciliation. Separate observations, hypotheses and uncertainty. Require support for material factual claims and explicit unknowns where evidence is missing. Allow source inspection beyond a summary when evidence is insufficient or contradicted.

Diagnosis and review are read-only unless specific reproduction/scratch edits are assigned. General project-edit permission does not give every worker production-write ownership. Report conflicting evidence before revising shared decisions.

## Verification and acceptance

The coordinator owns integration and final acceptance at its existing effort. Strong checks may be enough for mechanical edits. Add a separate reviewer only for a named risk or useful independence; do not duplicate a review the coordinator can adequately perform.

Review requirements, the diff, relevant source and checks—not just the implementer's summary. Findings need a location, trigger, impact and evidence. Prioritize credible correctness, security and data-integrity risks, not finding count. Distinguish defects from optional hardening and unsupported hypotheses.

Workers run focused checks. The coordinator checks these against the original requirement, not assumptions shared by the implementation and its tests. Use an independent expected result, regression reproduction or requirement-derived counterexample where needed. Check affected interactions after integration and tie results to the tested state. Return fixes to the owner; recheck affected risks instead of restarting every review.

Only the coordinator may revise acceptance criteria within user authorization. Never weaken assertions or redefine expected behavior merely to pass. Report suspect tests or conflicting requirements first. A successful process exit or a worker's “complete” is not acceptance.

## Failure and continuation

Judge the bounded assignment, not individual tool failures or an expected failing regression test. Permit local corrections within budget; stop repeating an unsuccessful approach without new evidence.

- **Accepted:** Required checks/evidence support the outcome. Reopen only for new evidence, changed dependencies or required review.
- **Blocked:** Resolve access, environment, tools or missing decisions within authority. A model switch is not the default fix.
- **Partial:** A checkpoint, turn limit or work budget was reached. Preserve progress; continuation needs a credible remaining plan within user limits.
- **Substantive failure:** Required behavior or a core assumption remains wrong after the bounded attempt. Distinguish missing evidence/specification from a reasoning limit. Repair the former; choose a more suitable model or effort for the latter, without walking every rung.

After one substantive non-trivial Luna failure, escalate rather than retrying the same assignment on Luna. Preserve evidence and partial work. For other workers, justify any renewed attempt by a changed approach, new evidence or a suitable configuration change. A review that finds defects has succeeded.

Before transferring write ownership, confirm the previous worker and writing commands have stopped. Preserve unrelated edits. Transfer the diff, exact failures, checks and open questions. If termination is uncertain, keep the successor read-only or on non-overlapping work.

## Waiting and cost control

Use event-driven waits when no useful independent coordinator work remains. Wait across active workers together and reuse cursors where supported. Use the longest suitable wait allowed by responsiveness rules, tool limits, deadlines and checkpoints; do not wake merely to preserve a cache.

An empty wait timeout proves neither failure nor health. Resume waiting without extra status reads, interruptions or replacement workers unless a checkpoint, blocker or exhausted budget warrants action. Do not substitute scheduled automations. At a due checkpoint, use one compact non-interrupting check if available; assess milestones and operations, not just a running flag. A process/work timeout that terminates a worker is different from a coordinator wait timeout.

For deployment plans, state models, efforts, ownership, dependencies, checks and why extra workers help. Count preparation, workers, input/cache use, reviews, failed attempts and integration. Do not repeatedly refine a specification when one capable owner could finish more cheaply. Keep API estimates separate from provider-specific allowance consumption.
