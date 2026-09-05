---
name: agent-deployment
description: Deploy cost-first Codex subagent teams with Astra for initial planning and final review, Luna for most implementation, and Sol for iterative review. Use when planning or executing multi-agent work or choosing a model and reasoning effort for each role. Do not use for single-agent model comparisons.
---

# Agent Deployment

Use this cost-first pipeline for complex work:

```text
Astra plan -> Luna implementation -> Sol review -> Luna correction -> Astra final review
```

Route most implementation to Luna, including difficult bounded work at `xhigh` or `max` reasoning. Use Sol as the reviewer during implementation. Reserve Astra for the initial plan and final review.

The user's explicit instructions take precedence over this skill. Preserve any model or reasoning effort the user requests. This skill selects deployment roles; it does not grant permission to create subagents. Delegate when the user's request or applicable instructions authorize subagent work.

## Roles

### Astra: initial planner and final reviewer (`gpt-6-astra`)

At the start, Astra may inspect the available context and repository to create the task graph. Its plan must define ownership, dependencies, interfaces, acceptance checks, review points, and integration risks. Astra should return assignments rather than implement them.

At the end, Astra reviews the integrated result, Sol's findings, and verification evidence against the original goal. It either accepts the result or returns bounded correction assignments for Luna. Send corrected work back to Astra for the final decision.

Keep Astra out of implementation unless the user requests a different role.

### Luna: default implementation worker (`gpt-5.6-luna`)

Assign Luna almost all implementation. Split work into bounded tasks with enough context for Luna to act without rediscovering the architecture.

Choose reasoning effort from the implementation burden:

- `low` or `medium`: mechanical edits, boilerplate, copy, lint, and routine changes.
- `high`: normal features, endpoints, integrations, and test work.
- `xhigh`: difficult but bounded debugging or changes across modules.
- `max`: the toughest implementation assignments when the plan, scope, and acceptance checks remain clear.

Raise Luna's reasoning effort before changing the implementation model. Use several Luna agents in parallel when their tasks do not share files or depend on unfinished outputs.

Each Luna assignment must include the objective, owned scope, required interfaces, acceptance checks, verification commands, dependencies, and files or behavior that must remain unchanged.

### Sol: iterative reviewer (`gpt-5.6-sol`)

Use Sol after each meaningful Luna implementation batch. Sol checks correctness, architecture fit, integration, missed requirements, and verification gaps.

Sol returns evidence-backed findings and bounded correction instructions. It should not rewrite the implementation by default. Send corrections back to Luna, then ask Sol to review the new result.

Use `high` for routine review and `xhigh` or `max` when the review requires deep debugging, cross-module reasoning, or subtle judgment.

### Terra: exception implementer (`gpt-5.6-terra`)

Terra sits outside the default pipeline. Use it when Luna is unavailable or when repeated Luna correction rounds show that a bounded assignment needs a capability bridge. Keep Sol as reviewer and Astra as final reviewer.

## Deployment workflow

1. Give Astra the full goal and ask for the initial task graph.
2. Convert the plan into bounded Luna assignments. Select `xhigh` or `max` for tough implementation rather than promoting the worker by habit.
3. Run independent Luna assignments in parallel.
4. Give each meaningful implementation batch to Sol for review.
5. Return Sol's correction instructions to Luna.
6. Repeat the Luna and Sol loop until Sol finds no material issue or the escalation rule applies.
7. Give Astra the complete result, review history, and verification evidence for final review.
8. If Astra finds a defect, route the bounded correction to Luna, review it with Sol when warranted, and return the result to Astra.

Keep integration ownership with the coordinating agent. Correct subtask outputs can still conflict when combined.

## Cost and escalation

Favor Luna because the cost gap can support more implementation attempts and higher reasoning effort. Estimate the complete workflow cost, including Luna retries, Sol reviews, and Astra gates.

Repository size does not select the implementation model. A large, precise task can still belong to Luna.

If Luna fails the same acceptance check in two correction rounds, ask Sol to rewrite the assignment with narrower scope and stronger evidence. If the revised assignment fails again, use Terra as the exception implementer or report that the task needs a user-approved deployment change. Do not move implementation to Astra by default.

## Review contracts

Give Sol the relevant plan, diff or artifact, Luna's explanation, and test output. Require findings with severity, evidence, and a concrete correction target. A clean review should say which acceptance checks Sol evaluated.

Give Astra the original goal, initial plan, integrated result, Sol review history, and verification evidence. Require a clear accept decision or a list of bounded corrections. Astra should judge the complete result rather than redo Sol's iteration review.

Match verification to the scope and impact of each change. Use targeted checks for small changes. Broaden testing when failures, shared interfaces, or unresolved concerns justify it.

## Communicating the deployment

When the user asks for a plan, present a compact table with task, role, model, reasoning effort, dependencies, and acceptance check. State the default pipeline and call out any Terra exception.
