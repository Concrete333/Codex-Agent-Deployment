---
name: agent-deployment
description: Reduce coordination overhead for authorized agent delegation and long-running scripts, tests, builds or database jobs. Use to choose bounded workers, arrange completion-triggered wake-up instead of polling, and verify results.
---

# Agent Deployment

Minimize total cost to an accepted result, including coordinator context, workers, checks and corrections. Preserve required accuracy; speed is not the goal. This skill does not authorize delegation, extra spending, billing changes or paid overflow.

## Decide whether to delegate

**Before launching an expected long-running command, including a test suite:** read [waiting.md](references/waiting.md) and establish its completion route before starting it, even when verification is only the last step of a coding task. For command-only work, load no other reference. Use native completion or the included queue helper; do not add an agent just to wait. Known-short commands stay direct, even full suites; use existing timing evidence, not a separate timing run. Do not load `docs/` for ordinary execution.

Keep small work local. Keep tightly coupled work with one owner, which may be a worker owning the entire component; do not split its dependent steps across agents. Prefer commands and scripts for deterministic work. Before spawning, identify a bounded workload the coordinator will stop doing and how its result can be checked. Include necessary source reading, integration and likely repair in that comparison; a cheap worker alone does not establish savings. Do not solve the whole assignment merely to make it delegable.

The coordinator owns consequential behavior, interfaces and acceptance. A worker can own a settled component through implementation, tests and corrections, or an independent evidence search. Large repositories, separate files and test-writing assignments are not inherently cheap or independent.

When reassessing prior results, verify the target identities and provenance first. Retain decision-level evidence on disk, not just aggregates. Reuse it when inputs are unchanged and it supports the new classification; do not rebuild merely to match an expected count. Matching totals do not establish historical membership.

**If staying local without a long-running job, stop here.** Do not load the references or write a delegation plan.

## When delegation is useful

- Use available, authorized models and efforts suited to the assignment and its checks. Follow explicit user preferences; compare total cost through acceptance. Keep the coordinator's model and effort unless asked to change them.
- Read [delegation.md](references/delegation.md) for ownership, verification and waiting. Consult [model-selection.md](references/model-selection.md) only when model choice is unresolved and recommendations would help; skip it for an explicit choice. Reuse guidance already read.
- For the bundled Claude wrapper, read [claude-cli.md](references/claude-cli.md); it supports Opus 5 only. Other models need a supported authorized route. Do not silently substitute or bypass adapter checks.
- For a software-managed CLI attempt with predefined checks, read [software-runner.md](references/software-runner.md). Prefer native delegation when its completion wait already suffices.

Workers receive their assignment and applicable project evidence, not routing policies or research. Do not load or search `docs/` during ordinary deployment; maintenance and audits may consult relevant documents.
