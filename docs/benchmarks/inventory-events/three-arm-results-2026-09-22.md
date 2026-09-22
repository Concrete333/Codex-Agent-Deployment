# Inventory: fresh solo Astra versus Luna and MiMo pipelines

**Luna Max plus Astra High acceptance cost 9.71% less than Astra High solo.**
MiMo produced no implementation before a provider stream error; its Astra
acceptor completed the work locally. That path cost at least 15.98% more on
captured usage, with possible unreported usage from the failed provider request.

| Configuration | Implementation/attempt | Astra acceptance or fallback | Captured total | Versus solo | Final independent checks |
|---|---:|---:|---:|---:|---|
| Astra High solo | $0.755888 | — | **$0.755888** | baseline | 27/27 methods |
| Luna Max + Astra High | $0.041546 | $0.640958 | **$0.682504** | 9.71% lower | 27/27 methods |
| MiMo thinking + Astra High | $0.004084 reported; incomplete | $0.872566 | **at least $0.876650** | at least 15.98% higher | 27/27 after full local implementation |

These are API-equivalent Codex estimates plus Kilo-reported cost, not bills or
subscription allowance. All five task sessions are included; shared fixture
preparation, supervisor setup and this analysis are excluded research overhead.
No paid retry or post-grading model repair occurred. One run per configuration
does not establish an average saving or a reliability rate.

## What actually happened

**Solo Astra** implemented the three modules and added 13 tests. Its public and
added suite passed 17 methods; the independent grader passed all 27. No separate
reviewer was added to this baseline.

**Luna** implemented all three modules and added six tests. It passed all 27
independent methods before Astra saw it. Astra inspected the contract and diff,
added six acceptance tests in a new file, and accepted without changing any
implementation code or original worker tests. Final added tests: 12 passing.
Acceptance cost 93.91% of this pipeline. The combined saving was $0.0733844.

**MiMo** completed two reading/tool responses, then the event stream reported
`APIError: Stream error occurred`, with `AI_InvalidResponseDataError` and
`isRetryable: false`. The process exited 1 after 594.66 seconds. It produced no
edits, added tests or valid handoff. The wrapper marked failure and released
ownership after confirmed termination. Astra then implemented all three modules
and 13 tests itself; its acceptance-stage cost is therefore implementation plus
review, not verification of a useful cheap-worker artifact.

The failed MiMo candidate remained the starter. Its independent grade contains
11 failures and 28 errors across 27 methods (subtests can produce multiple
failures within a method). Do not subtract those counts to infer passed methods.

This is a provider/runtime failure, not evidence that MiMo wrote incorrect code
or lacks the task's reasoning ability. It does count against reliability of this
deployment route and against total cost to a result.

## Did the larger output allowance help?

The experiment requested `KILO_EXPERIMENTAL_OUTPUT_TOKEN_MAX=65536`, retained
thinking and normal Kilo capabilities, and removed the iteration cap. The
30-minute stage timeout did not fire. No `length` stop was recorded this time;
the last completed step reports `tool-calls`, followed by the stream error.

There is no completed usage record for the failed request. Its token consumption,
effective output ceiling and any billed cost are unknown. The two observed
step costs sum to $0.0040837386; that is captured spend, not a complete bill.
This run neither proves the override fixed the earlier 32k length stop nor
establishes that the override caused the stream error. Keep it experimental;
do not raise the everyday default based on this result.

## Measurement integrity

The [pre-registered protocol](three-arm-protocol-2026-09-22.md) used the same
implementation contract and original inventory source bytes for all arms.
Software supplied the brief directly; no model was paid to paraphrase it.
Fresh acceptance sessions used identical prompts for Luna and MiMo. Necessary
local completion was permitted and counted, but no second worker was authorized.

Coverage increased from the README's 21 methods to **27**, including a seeded
80-scenario lifecycle matrix inside one method. Correct and alias controls
passed; the starter and nine distinct broken variants failed before inference.
Private checks were never fed back to task models. Current artifacts were
regraded successfully during this offline audit. Protected files were unchanged;
the host checked write scope and retained original worker evidence through review.

All native process receipts show exit zero, no timeout and resolved ownership;
MiMo's failed exit is retained separately. The Kilo lock is absent. The supervisor
saved its terminal receipt and queued one completion message. Waiting occurred
in software, not parent-model polling. No unexpected native coordination calls
appear in the audited usage records.

| Session | Input, including cache | Cached input | Output, including reasoning | Reasoning | Responses |
|---|---:|---:|---:|---:|---:|
| Solo Astra | 99,113 | 63,488 | 6,723 | 307 | 6 |
| Luna implementation | 329,312 | 281,600 | 21,976 | 15,531 | 13 |
| Astra acceptance of Luna | 115,937 | 74,368 | 3,018 | 484 | 6 |
| Astra fallback after MiMo | 113,448 | 64,896 | 6,443 | 653 | 6 |

Native own-response usage reconciles exactly to recorded cumulative totals.
Effective configurations were Astra High and Luna Max. Frozen per-million rates
were Astra $10 uncached/$1 cached/$50 output and Luna $0.20/$0.02/$1.20; no cache
writes or long-context threshold occurred. Luna's combined route used more raw
tokens than solo despite its lower price-weighted cost.

Elapsed times were 4.3 minutes solo, 19.8 minutes Luna plus acceptance, and 13.9
minutes MiMo plus fallback. Arms ran concurrently in isolated checkouts; shared
machine/provider contention means latency is descriptive, not a speed ranking.
Codex CLI was 0.155.0-alpha.9.2; Kilo was 7.7.6.

## Interpretation

The small saving survives comparison with **ordinary solo implementation and
self-review**, not only an Astra-plus-Astra baseline. However, the old 27.65%
README result cannot be directly pooled with this one: coverage, runtime date,
acceptance context and permitted repair behavior differ.

The main remaining cost is substantive acceptance, not polling or worker
implementation. This clean Luna submission does not show that omitting review
or using a cheaper reviewer would preserve accuracy. The failed MiMo route
should not be presented as a cost-effective alternative on this evidence.

Do not add more operational skill rules from this one result. A replicated
comparison on a different settled component would be stronger evidence than
tuning this fixture until one route wins.

## Retained evidence

`local-three-arm.json` locates `inventory-three-3e113ce938c1456aa3dc3d76dea0f43f`.
Its `accounting.json`, per-arm receipts/grades, original candidates and native
rollouts retain the full evidence. `three_arm_analysis.py` reproduces the offline
accounting, receipt checks, file comparisons and regrading without inference.

- Solo Astra: `01a0c844-8c1f-7ab1-ac80-ca10e55aaedb`
- Luna: `01a0c844-8c1f-7523-abd7-97618c214678`
- Astra accepting Luna: `01a0c854-9af5-7532-ac22-da403f19f870`
- Astra after MiMo: `01a0c84d-a0b0-7372-bc82-22d01f6b9152`
- Kilo run: `20260922-093625-0207351e`
- Kilo session: `ses_f37bb61c1ffeUGj6HSLZV2HeaK`
