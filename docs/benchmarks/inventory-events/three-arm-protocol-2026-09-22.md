# Fresh inventory comparison: solo Astra, Luna, MiMo

Authorized configurations, one run each:

| Arm | Implementation | Acceptance |
|---|---|---|
| Solo | Astra High | Same session's development checks and self-review |
| Luna | Luna Max | One fresh Astra High session; necessary local corrections allowed |
| MiMo | MiMo-V2.6-Pro thinking through Kilo | Identical Astra High acceptance prompt and correction authority |

Software supplies the same fixed implementation contract to all three. It does
not pay Astra to restate a settled assignment. No separate reviewer is added to
solo. This compares total task execution through the specified verification
path, not equal numbers of model sessions or spontaneous routing by the skill.
The two acceptance sessions load the same deployment skill and delegation guide.
Implementers do not load routing guidance or benchmark research.

The task/specification/starter bytes match the README inventory task. Its original
21 public/independent methods remain unchanged. Six new private methods check
generator mutation/replay isolation, iterator failure after each hold operation,
replay after hold-ID reuse, failed preview receipt isolation, snapshot isolation,
and a seeded 80-scenario lifecycle matrix. Matrix outcomes use independently
calculated literal quantities, not the reference implementation as an oracle.

There are **27 test methods**, not 107 independent tests. The matrix and existing
subtests exercise multiple scenarios within methods. No new features or hidden
requirements are introduced. Qualification before inference requires the correct
and alias references to pass, and the starter plus nine distinct mutants to fail.
This remains a synthetic task with a familiar core, not an unseen-task study.

## Runtime and fairness

- Fresh isolated checkouts and sessions, same source and ownership boundaries.
- Same implementation contract, public checks, result schema and instruction to
  implement/test in small increments. Workers receive no prior solutions,
  private tests or historical findings.
- Two independent delegated arms, each with exactly one worker attempt. Host
  dispatch means no model sits waiting. Three arms launch concurrently; shared
  machine/provider contention is a caveat, so latency is descriptive only.
- Astra is High throughout; Luna is Max; MiMo is thinking. No model substitution.
- Thirty-minute timeout per model stage, no iteration cap for MiMo. Maximum five
  sessions: three implementers and two acceptors. These are per-stage limits,
  not equal aggregate compute budgets or spending caps.
- A failed worker's safe, terminated partial artifact may be completed locally
  by its one authorized Astra acceptance session. Count this as fallback/repair,
  not successful cheap implementation. No second worker or automatic retry.
- Independent checks run before and after acceptance, without revealing their
  results to the task models. Preserve originals. No post-grading paid repair.
- Protected-file hashes and write-scope checks apply to all arms. Unresolved
  process ownership prevents dependent acceptance. A partial or blocked final
  handoff cannot qualify merely because the grader passes.

## Kilo preparation

The earlier response stopped at `reason: length`, with 32,001 reasoning tokens.
The wrapper now preserves the final finish reason and rejects a terminal length
stop even if older text claims completion. Its implementation prompt asks for
small tested increments. Fifty-three offline wrapper tests passed, including a
length-stop fixture; this does not prove a model will follow the new instruction.

[Kilo documents](https://kilo.ai/docs/customize/context/context-condensing#cli)
`KILO_EXPERIMENTAL_OUTPUT_TOKEN_MAX` as overriding the default 32,000 output
ceiling. Local Kilo 7.7.6 model metadata advertises 131,072 output tokens for
MiMo-V2.6-Pro. This experiment requests **65,536** through that environment
variable, for this batch only. Record the requested setting; the preflight
does not prove the provider will honor it. No global default, permissions,
authentication, billing, compaction or model-selection setting is changed.

The [cost guidance](https://kilo.ai/docs/getting-started/rate-limits-and-costs)
supports scoped context and automatic caching. Its generic recommendation to
use smaller output limits is not applied blindly to a measured length stop.
Compaction manages conversation history; it is not a substitute for resolving
response truncation. Normal Kilo tool capabilities remain available, but the
assignment prohibits extra agents and external services. CLI/tool scaffolds
necessarily differ between vendors.

## Accounting and interpretation

Freeze task, checker, runtime, policy, prompt, model settings and pricing before
launch. Preserve session IDs, complete logs, receipts, original worker code,
final code and per-stage timings. Reconcile native response usage; include all
Kilo-reported step costs, including failures and any compaction activity exposed
by telemetry. Unknown costs remain unknown, not zero. Record actual models and
efforts, output stops, worker success, correction files and final check results.

Report total execution cost and correctness together, with implementation and
acceptance/repair costs separate. Research preparation, qualification and later
analysis are excluded and identified, not silently counted as free coordination.
API-equivalent estimates are not subscription allowance. No claim that one
successful run proves reliability or a universal saving. Compare these fresh
arms primarily with each other; the older README pair used narrower coverage,
different runtime dates and separate read-only reviews without repair.

Implementation: `three_arm.py prepare` qualifies/freezes without inference;
`run` performs the batch through existing transports. `local-three-arm.json`
points to retained private evidence. Superseded no-inference preflights remain
on disk. One supervisor queues completion after all arms terminate.
