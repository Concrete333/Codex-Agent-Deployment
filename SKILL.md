---
name: agent-deployment
description: Select the appropriate Codex model for a complex task and each of its subagents. Use when planning or executing multi-agent work, assigning model overrides, or checking whether a delegation plan balances capability, uncertainty, and cost. Do not use for ordinary single-agent model comparisons.
---

# Agent Deployment

Choose models per bounded task, not once for the entire project. Optimize for the expected total cost of a correct result, including token use, retries, supervision, and rework. A higher per-token price can cost less when it prevents failed attempts or shortens a long investigation.

The user's explicit instructions take precedence over this skill. Preserve any model the user explicitly requests. This skill selects models; it does not itself authorize delegation. Spawn subagents only when the user's request or applicable instructions call for subagents, delegation, or parallel agent work.

## Model ladder

### Luna — Mechanical work (`gpt-5.6-luna`)

Use when the target and method are already known and completion is easy to verify: renames, simple edits, boilerplate, copy changes, type fixes, lint fixes, and repetitive modifications.

Test: **We know exactly what needs to be done; do it cheaply.**

Example: Rename a component across the project, update its imports, and fix resulting lint errors.

### Terra — Everyday development (`gpt-5.6-terra`)

Use for normal software development with familiar patterns and bounded decisions: regular screens, endpoints, integrations with existing APIs, tests, and straightforward features.

Test: **The task needs ordinary engineering judgment, but the shape of the solution is clear.**

Example: Add an account-deletion endpoint and connect it to the existing settings screen.

### Sol — Complex development (`gpt-5.6-sol`)

Use when the implementation itself is difficult: non-obvious debugging, coordinated changes across modules, complex features, architecture-aware code review, or root-cause fixes in an existing system.

Test: **We broadly know what must be achieved, but implementing it correctly is hard.**

Example: Find why offline sync occasionally creates duplicates, fix the root cause, and add regression tests.

### Astra — Figure it out and get it done (`gpt-6-astra`)

Use when even determining the right work is difficult: unknown or poorly localized bugs, architectural changes, large migrations, infrastructure and DevOps, cross-system investigations, ambiguous requirements with material tradeoffs, and nuanced review work. Astra also fits long tool-driven workflows where each observation determines the next action: inspect, run, observe, revise, and verify.

Test: **The agent must discover the problem, choose the approach, and then deliver the solution.**

Example: Investigate an unlocalized failure, reproduce it, identify the root cause, choose and implement the fix, and iterate through verification.

## Deployment method

1. Decompose the request into independently ownable tasks with explicit outputs and acceptance checks. Separate discovery, design, implementation, review, and mechanical follow-through when they have different difficulty.
2. For each task, identify what is unknown. Distinguish difficulty in **figuring out what to do** from difficulty in **doing it**.
3. Assign the lowest tier that clears the task's uncertainty and execution burden.
4. Promote a task when it has unclear ownership, weak reproduction steps, architectural tradeoffs, subtle correctness or safety risks, high rework cost, or a review that depends on nuanced inference.
5. Demote a task when a stronger agent has already converted it into a precise, bounded instruction with objective validation.
6. Keep integration ownership with an agent capable of evaluating the whole result. Do not assume that independently correct subtask outputs compose correctly.

For mixed work, use Astra or Sol to investigate, define interfaces, or integrate; use Terra for routine implementation; and use Luna for deterministic follow-through. Do not assign every subagent the coordinator's tier merely because the overall project is complex.

Repository size and context length do not determine the tier. Promote work in a large repository when unknown relationships or long-horizon decisions require stronger reasoning. Keep precise, verifiable work at the lower tier that can own it.

Estimate total expected cost from token use, retries, supervision, and rework. Promote the task when a cheaper worker would need extensive supervision, lacks enough context to notice failure, or could cause costly rework.

If a named model is unavailable, choose the nearest available model with at least the required capability and state the substitution.

## Astra assignment contract

When Astra owns or coordinates work, state the objective, owned scope, dependencies, required output, acceptance checks, and stopping condition. State whether delegation is authorized, which work can run in parallel, and whether subagents may delegate again.

Tell Astra to carry authorized work through implementation and proportionate verification. Allow routine, reversible assumptions. Ask for user input when missing information could materially change correctness, scope, or authorization.

Match verification to the scope and impact of the change. Give Astra targeted checks for small changes. Broaden or repeat testing when a failure, new change, or unresolved concern justifies it.

## Communicating the plan

When the user asks for a plan, present a compact assignment table with: task, model, reason, dependencies, and acceptance check. When actively delegating, keep the explanation brief and put the same boundaries and acceptance criteria in each subagent's prompt.
