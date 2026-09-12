---
name: agent-deployment
description: Guide Codex orchestrators in choosing Luna, Terra, Sol or Opus 5 workers, assigning bounded work and verifying results. Use when planning, executing or auditing authorized delegation.
---

# Agent Deployment

Minimize total cost to an accepted result, including coordinator context, workers, checks and corrections. Preserve required accuracy; speed is not the goal. This skill does not authorize delegation, extra spending, billing changes or paid overflow.

## Decide whether to delegate

Keep small work local. Keep tightly coupled work with one owner, which may be a worker owning the entire component; do not split its dependent steps across agents. Prefer commands and scripts for deterministic work. Before spawning, identify a bounded workload the coordinator will stop doing and how its result can be checked. Include necessary source reading, integration and likely repair in that comparison; a cheap worker alone does not establish savings. Do not solve the whole assignment merely to make it delegable.

The coordinator owns consequential behavior, interfaces and acceptance. A worker can own a settled component through implementation, tests and corrections, or an independent evidence search. Large repositories, separate files and test-writing assignments are not inherently cheap or independent.

**If staying local, stop here.** Do not load the references or write a delegation plan.

## When delegation is useful

- Workers may use only **Luna, Terra, Sol or Opus 5**. Luna uses **Max only**. No Astra or Fable workers, including reviewers, forks or nested delegates. Keep the orchestrator's model and effort; retain open-ended diagnosis, architecture and difficult coupled reasoning locally.
- If choosing a worker or effort, read [model-selection.md](references/model-selection.md). Skip it when both are already fixed within the allowed configurations. Read [delegation.md](references/delegation.md) for ownership, verification and waiting. Reuse guidance already read.
- For authorized Opus 5 use, also read [claude-cli.md](references/claude-cli.md) and use its wrapper. Do not silently substitute unavailable configurations.
- For a software-managed CLI attempt with predefined checks, read [software-runner.md](references/software-runner.md). Prefer native delegation when its completion wait already suffices.

Workers receive their assignment and applicable project evidence, not routing policies or research. Do not load or search `docs/` during ordinary deployment; maintenance and audits may consult relevant documents.
