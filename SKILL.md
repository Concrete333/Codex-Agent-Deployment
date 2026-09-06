---
name: agent-deployment
description: Route authorized subagent work to Luna at max for context-heavy, large-repository, or repetitive tasks and to Astra at low for harder well-specified implementation where correctness matters more. Use when planning or executing delegated work or reviewing deployment efficiency. Do not use for single-agent model comparisons.
---

# Agent Deployment

Minimize total usage while meeting the task's correctness and safety requirements. Model price alone does not determine the route. User model choices, effort choices, budgets, and authorization take precedence. This skill does not authorize delegation.

## Routing policy

### Luna at max (`gpt-5.6-luna`)

Use Luna only at `max` reasoning effort. Do not assign Luna at `low`, `medium`, `high`, or `xhigh`.

Choose Luna when the assignment is dominated by at least one of these burdens:

- Reading or loading a large amount of context.
- Exploring or mapping a large or unfamiliar repository.
- Repetitive, mechanical, or bulk work with an objective check.

Luna may investigate, extract evidence, or implement when one of those burdens dominates. Give it clear boundaries, entry points, search targets, and acceptance checks instead of sending the conversation history or a repository dump.

### Astra at low (`gpt-6-astra`)

Choose Astra at `low` for harder implementation when the task is already well specified and correctness matters more than the model-cost difference. This includes subtle logic, consequential state changes, difficult integration, and work where a plausible but wrong patch would be expensive.

Settle the contract before dispatch: expected behavior, owned scope, interfaces, compatibility requirements, and acceptance checks. Do not pay Astra to rediscover broad repository context that Luna can map first.

When a task combines broad discovery with difficult implementation, use Luna at `max` to produce a concise evidence packet, then give the specified implementation to Astra at `low`.

### Sol review (`gpt-5.6-sol`)

Sol is optional. Use one consolidated independent review when risk, unfamiliarity, or cross-module effects justify it. A Sol review replaces duplicate detailed review by the coordinator; it is not a mandatory extra stage.

### Terra

Do not assign Terra under this policy.

## Smallest useful team

- Finish trivial work locally when delegation would cost more than the task.
- Default to one worker. Add another only for independent work with settled interfaces and separate ownership.
- Keep tightly coupled work with one owner. Do not create agents merely to occupy available slots.
- The coordinator owns integration and final acceptance unless the user requires an independent reviewer.

## Assignment contract

Send a self-contained assignment, normally no more than 500 words:

```text
Outcome and scope:
Owned files; dependencies and interfaces:
Context entry points and search targets:
Constraints and behavior to preserve:
Acceptance checks and commands:
Return: changed files or evidence, check results, unresolved risks (normally <=200 words).
```

For Astra implementation, include the settled design and the smallest evidence packet needed to act. For Luna exploration, ask for exact file, symbol, command, and failure references that another worker can use without repeating the search.

Use fresh workers without inherited history where supported. Preserve essential user constraints explicitly. Point to source files and evidence rather than pasting large content. For substantial history-heavy work, read [context-management.md](../../context-management.md).

## Escalate after one Luna failure

A substantive Luna failure is one failed required acceptance check, a wrong architectural assumption, a missed core requirement, or an incomplete non-trivial result after Luna has used its first assignment to investigate and self-correct.

After one substantive failure on a non-trivial task:

1. Preserve the exact failure and useful evidence.
2. Stop Luna correction rounds for that task.
3. Settle or narrow any remaining contract ambiguity.
4. Assign the implementation to Astra at `low` with Luna's evidence and the failed acceptance check.

Do not spend another Luna activation hoping for a different result. A clearly transient tool or environment failure may be rerun without counting as a model failure. For a trivial Luna failure, the coordinator may make the small correction directly.

If Astra at `low` also fails, inspect the concrete cause before changing effort or adding agents. Any further escalation needs evidence that the current model or effort is the limiting factor.

## Context and handoffs

- Reuse inspected evidence until a relevant edit or observation invalidates it.
- Let Luna read the large source set once. Hand Astra a bounded map of relevant files, symbols, invariants, and exact failures.
- Batch findings into one correction or review packet. Avoid acknowledgement messages, repeated status reads, and full passing logs.
- Workers run focused checks before returning. Run broader integrated checks only when the change, a failure, or unresolved risk justifies them.
- Stop accepted work from being reopened unless a dependency changed or new evidence appeared.

## Communicating the deployment

When the user asks for a plan, list each task, model, effort, reason, dependencies, and acceptance check. State why any Sol review or additional worker is worth its context and handoff cost.
