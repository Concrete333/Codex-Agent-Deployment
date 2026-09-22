# Fresh repeat: Sol solo, Sol + Luna, Sol + MiMo

Sol High + Luna Max cost **19.8% less** than fresh Sol High solo on this run,
including Sol's review and repair. MiMo produced no edits or valid handoff;
Sol completed that arm locally. Its final pass is not successful delegation.

## Frozen results

| Setup | Preparation | Worker | Solo implementation or acceptance/repair | Total | Versus solo | Final checks |
|---|---:|---:|---:|---:|---:|---|
| Sol High solo | — | — | $0.806540 | **$0.806540** | baseline | 254/254 |
| Sol High + Luna Max | $0.116913 | $0.076002 | $0.453974 | **$0.646889** | 19.8% lower | 254/254 |
| Sol High + MiMo-V2.6-Pro thinking, uncapped | $0.120390 | $0.044343 | $0.588222 | **$0.752955** | 6.6% lower | 254/254 after full local implementation |

Codex figures are API-equivalent estimates from reconciled response usage;
MiMo is Kilo's reported cost. These are not subscription allowance measurements.
All task-model stages are counted, including the failed worker. Benchmark setup,
supervision and analysis are excluded research overhead. The MiMo total's small
advantage over solo cannot establish a delegation benefit: it bought no code.

All final submissions passed 150 visible and 104 held-out cases and preserved
protected files. Added tests passed: solo 15, reviewed Luna 8, Sol fallback 8.
Summed model-stage elapsed times were 10.8, 19.5 and 17.5 minutes respectively.
Speed was not optimized.

## What the workers delivered

**Luna:** all six adapters, a shared helper and seven tests; valid complete
handoff. Passed all 254 cases before review. Sol changed only the XML adapter
and test file, adding a regression for a DOCTYPE-like string inside CDATA.
The final eight-test suite passed. Review and repair cost $0.454, about 70% of
this pipeline's total; the worker itself was about 12%.

**MiMo:** no changed files, tests or valid handoff. The CLI exited zero, but the
wrapper correctly marked the attempt failed. There was no iteration cap and
the 30-minute timeout did not fire. The sixth and last recorded generation
ended with `reason: length`, reporting 32,001 reasoning tokens and zero output
tokens in that response. This is evidence of a generation-length stop, not the
old 30-step cap. The trace alone does not establish which provider/CLI setting
imposed that response limit. No automatic retry was made.

After confirmed worker termination, Sol's pre-authorized acceptance stage
implemented all six adapters, helper and tests itself. Its cost is therefore
implementation plus review, not a cheap reviewer completing MiMo's work.

## Accuracy qualification beyond the frozen score

Sol's Luna review identified an XML distinction not covered by the 254 cases:
`<!DOCTYPE` inside a CDATA memo is literal text, not a declaration. The task
forbids declarations, but does not exclude CDATA. We replayed the exact input
from Sol's new regression against all final submissions and the reference:

| Submission | Literal preserved |
|---|---|
| Solo Sol | Yes |
| Luna before review | No |
| Luna after Sol review | Yes |
| Sol fallback after MiMo failure | No |
| Frozen reference | No |

This exposes a reference/contract discrepancy and a coverage gap; the reference
is not proof that the rejection is correct. Keep it as a post-hoc result, not an
extra held-out success or a retroactive change to the frozen score. No model was
rerun or candidate repaired after external grading. All three passed the frozen
checks, but this does **not** establish equal overall accuracy.

The previously observed bare-CSV-quote issue was explicit in this run's contract
and covered by valid and invalid controls. All three final submissions passed
those cases.

## Measurement and recovery

[Protocol](repeat-protocol-2026-09-22.md): fresh sessions and identical starting
sources; common coordinator policy for both delegated arms; solo/Luna/MiMo order
frozen before launch; private checks withheld from all task models. One worker
attempt per delegated arm. Software waited between stages and submitted one
completion notification; there were no model calls for worker-wait polling.

Every model-stage receipt confirms exit, no timeout and resolved ownership.
Kilo's ownership lock was removed. Its exit was not mistaken for acceptance.
Native Codex usage reconciles to the own-thread totals; resumed acceptance
counters are cumulative and were not added twice. Recorded configurations were
Sol High and Luna Max. Kilo's manifest records MiMo thinking with `steps: null`.

| Session | Input tokens | Cached input (included) | Output tokens | Reasoning (included in output) | Responses |
|---|---:|---:|---:|---:|---:|
| Solo Sol | 531,070 | 454,400 | 15,905 | 6,519 | 16 |
| Luna arm: Sol | 321,728 | 269,568 | 12,721 | 7,244 | 13 |
| Luna worker | 965,131 | 878,848 | 34,307 | 22,777 | 20 |
| MiMo arm: Sol | 282,591 | 216,320 | 17,850 | 7,049 | 10 |

The Luna route used more aggregate raw tokens than solo while costing less under
the frozen model prices. Do not present price-weighted savings as total-token
reduction. Uncached/cached/output rates per million were Sol $4/$0.40/$20 and
Luna $0.20/$0.02/$1.20; no cache writes or long-context pricing threshold occurred.
Kilo's six reported step costs sum to its $0.044343084 receipt.

The initial grader could not print MiMo's Unicode-rich failure list through
Windows CP1252. The original failed grade is retained. Offline regrading with
`PYTHONUTF8=1` changed only reporting, not the candidate or cases: the unchanged
stubs passed 8/150 visible and 0/104 held-out. All final grades were independently
rechecked successfully. No extra paid calls were used for recovery or analysis.

## Takeaways

- Luna delivered useful work at lower combined estimated cost again: 19.8% here,
  versus 30.1% in the earlier comparison. Those runs used different coverage and
  must not be pooled as identical repetitions or a general savings rate.
- Retain substantive acceptance. Luna passed every frozen test before review,
  yet Sol found a real XML handling distinction outside that suite.
- Uncapped steps do not guarantee completion. MiMo's failed attempt remains in
  both the reliability record and total cost; a larger step allowance would not
  address the observed response-length stop.
- A final pass after fallback must identify who actually implemented the code.
- This tests forced, host-managed delegation on a familiar bounded fixture,
  not spontaneous routing, unseen-task performance or an isolated model ranking.

## Reproduction evidence

`analyze_repeat.py` performs offline receipt checks, token reconciliation,
regrading, artifact comparison and the post-hoc CDATA probe. The ignored
`local-repeat.json` locates the retained run directory, whose `accounting.json`
contains machine-readable results and rollout paths.

- Run: `deployment-repeat-2e107320652b4ed4b28cab8673951d1a`
- Solo Sol: `01a0c65b-1eb2-7160-8604-175e605ade88`
- Luna coordinator: `01a0c665-066b-7f30-a123-01a0622651ca`
- Luna worker: `01a0c666-6010-7660-b7e4-ec8d3b482956`
- MiMo coordinator: `01a0c676-ec07-7fe3-bf44-5a12356ec640`
- Kilo run: `20260922-011612-bb5fb563`
- Kilo session: `ses_f398784edffeDAWnR3Sk6bQ3iU`

CLI versions: Codex `0.155.0-alpha.9.2`, Kilo `7.7.6`. One run per condition,
with different CLI scaffolds and no estimate of run-to-run variance.
