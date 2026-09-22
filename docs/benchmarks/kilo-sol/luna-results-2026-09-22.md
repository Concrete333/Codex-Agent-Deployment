# Sol High + Luna Max: 30.1% lower estimated cost in one run

The host-managed Sol High -> Luna Max -> resumed Sol High pipeline completed
without a runtime recovery or model retry. Both the worker submission and final
accepted submission passed 146 visible, 98 held-out and six added tests. All
eight worker-owned files are byte-identical before and after Sol acceptance:
**no coordinator corrections were made**.

| Arm | Coordinator | Worker | Total estimate | Frozen cases |
| --- | ---: | ---: | ---: | ---: |
| Sol High solo, retained baseline | $0.776054 | — | **$0.776054** | 244/244 |
| Sol High + MiMo, capped at 30 steps | $0.683719 | $0.149495 | **$0.833214** | 244/244 after repair |
| Sol High + Luna Max | $0.450906 | $0.091826 | **$0.542732** | 244/244 without repair |

The new pipeline is **30.065% cheaper** than the saved solo baseline, including
Sol assignment preparation, Luna implementation and Sol acceptance. It was
slower: about 18.8 minutes versus 11.1 minutes solo. Time was not the target.
The [uncapped MiMo follow-up](uncapped-results-2026-09-22.md) is now complete:
$0.683925, with a complete handoff but an unresolved post-hoc reference mismatch.

## Cost and usage

| Stage | Estimated cost | Process duration |
| --- | ---: | ---: |
| Sol High preparation | $0.130723 | 101.403 s |
| Luna Max implementation | $0.091826 | 771.957 s |
| Sol High acceptance | $0.320182 | 253.675 s |

| Recorded usage | Sol coordinator, both stages | Luna worker |
| --- | ---: | ---: |
| Input, including cached | 245,349 | 1,415,890 |
| Cached input | 196,864 | 1,320,192 |
| Output, including reasoning | 8,911 | 38,569 |
| Model responses | 12 | 28 |

All per-response usage reconciles with session totals. The rollouts confirm
`gpt-5.6-sol / high` and `gpt-5.6-luna / max`. Resumed Sol totals are cumulative
and were not counted twice. The host waited between model sessions; no Sol
session was kept active to poll the worker. All three processes exited normally,
without timeout or unresolved ownership.

The pipeline used about 2.9 times as many total input tokens as solo, but moved
much of the work to cheaper Luna tokens. This is **estimated cost reduction,
not raw-token reduction or measured subscription-allowance savings**. Estimates
use the existing per-million benchmark rates: Sol $4 input/$0.40 cached/$20
output; Luna $0.20 input/$0.02 cached/$1.20 output. Research preparation,
supervision, analysis and the original baseline's harness recovery are excluded.

## Verification and limits

Luna returned a complete structured handoff and explicitly identified stray
quotes in unquoted CSV fields as malformed. Sol reviewed the candidate and
accepted it without edits. The same post-hoc malformed-quote probe used for the
MiMo analysis raises `ValueError` on Luna's unmodified submission. Neither
model was supplied that probe, the earlier solutions or private grading results.
It is a known follow-up probe, not a new held-out task.

This result supports bounded delegation on this particular fixture. It does
not establish general superiority, a safe reduction in acceptance, or that the
skill alone caused the saving. One run per arm, a reused task and a retained
baseline do not control for run-to-run variation. Runtime/policy differences
from MiMo, including the absent step cap, are in
[the frozen protocol](luna-protocol-2026-09-22.md).

## Evidence

Local root: `C:/Users/cwbec/AppData/Local/Temp/sol-luna-9bbb474ae40e409a869dcd3fce5e516c`.

- `result.json`: pipeline outcome and both session IDs.
- `accounting.json`: reconciled usage, stage costs, byte comparisons and quote probe.
- `worker-verified-grade.json`, `delegated-verified-grade.json`: scope and tests.
- `worker/worker-final.txt`, `delegated/accept-final.txt`: separately retained claims.
- Sol session: `01a0c637-ac02-7de1-b258-a6a56df84740`.
- Luna session: `01a0c639-3858-7153-97fe-74e1735888c3`.

`analyze.py --luna` reproduces the offline checks and accounting, without model calls.
