# Luna generation comparison on the same CLI

Both Luna Max workers passed all 27 independent inventory test methods before
Astra High reviewed them. Neither needed implementation repairs. GPT-6 Luna's
worker cost was 52.72% lower; its complete pipeline cost was 12.58% lower.

## Results

| Configuration | Implementation | Astra High acceptance | Captured total | Independent checks |
|---|---:|---:|---:|---|
| GPT-5.6 Luna Max + Astra High, 23 September | $0.035770 | $0.563904 | $0.599674 | 27/27 before and after review |
| GPT-6 Luna Max + Astra High, 23 September | $0.016914 | $0.507324 | $0.524238 | 27/27 before and after review |
| Astra High solo, 22 September; earlier CLI | $0.755888 | No additional reviewer | $0.755888 | 27/27 final |

The solo result is an existing same-task baseline, not a fresh same-CLI control.
Unrounded pipeline totals are $0.59967432 and $0.52423786. Methods include
multi-scenario checks; their count is not a count of independent tasks.

The repeated GPT-5.6 worker implemented three modules and added five tests.
Astra added five acceptance tests without changing the implementation or worker
tests. All 14 public, worker and acceptance tests passed. The GPT-6 submission
similarly required no implementation repairs; its combined suite passed 16 tests.
No extra paid correction session was used in either pipeline.

## Cost interpretation

Of the $0.07543646 pipeline reduction, $0.01885646 came from the worker and
$0.05658 from review. Thus **75% of the reduction came from different Astra
review usage**, not the worker bill. One run cannot establish that GPT-6 Luna
causes cheaper reviews.

| Worker measurement | GPT-5.6 Luna Max | GPT-6 Luna Max |
|---|---:|---:|
| Input, including cached input | 271,980 | 415,053 |
| Cached input | 230,656 | 361,216 |
| Output, including reasoning | 19,077 | 15,836 |
| Reasoning output, included above | 12,871 | 8,826 |
| Model responses | 12 | 19 |
| Implementation seconds | 380.417 | 363.057 |

GPT-6 used more input but less output. At the old Luna token rates, its observed
usage would cost $0.03699492, about 3.42% more than this GPT-5.6 repeat. Its lower
worker bill therefore does not demonstrate lower price-normalized token cost.

The GPT-5.6 acceptance session used 139,839 input tokens, including 114,304 cached,
and 3,885 output tokens, including 556 reasoning, across seven responses. GPT-6's
review used 162,706 input, including 136,704 cached, and 2,212 output, including
186 reasoning, across eight responses. Total elapsed time was 529.37 versus
457.60 seconds. Review remains the dominant cost in both pipelines.

The original GPT-5.6 pipeline cost $0.682504. Repeating the same model already
lowered that by 12.14%, illustrating why the first historical comparison cannot
isolate a model-generation effect.

## Controls and limits

The [repeat protocol](luna56-repeat-protocol-2026-09-23.md) retained the frozen
task, prompts, policy, grader, timeouts and scope. Both September 23 runs used
CLI `0.155.0-alpha.16`. Grader qualification passed before launch; post-run
fingerprints, protected files and change scope matched. Effective rollout
configurations were `gpt-5.6-luna/max` and `gpt-6-astra/high` for the repeat.
Recorded usage reconciled; no session recorded cache writes, coordination calls
or a request above the 272k pricing boundary.

The repeat's worker and reviewer exited zero without timeout or uncertain
ownership. The supervisor and stage processes were absent at inspection, and
the terminal notification was queued once. Independent grades and source review
confirmed completion; the notification alone was not treated as success.

These are single runs on one synthetic task, not a general capability ranking.
Run order, caching and service conditions were not controlled. Costs are
API-equivalent estimates, not bills or Codex allowance consumption; preparation
and analysis are excluded. No routing defaults or acceptance requirements change
on this evidence alone.

## Evidence

The ignored `local-luna56-repeat.json` locates batch
`inventory-gpt-5.6-luna-1926bc3af94c488eac123cd559aa63cd`, retaining the manifest,
receipts, original submissions, grades and `accounting.json`.

- GPT-5.6 worker session: `01a0cdf5-16b9-7a12-bed5-eef82cd0d225`.
- Astra acceptance session: `01a0cdfa-e627-7c50-979b-f168316b4462`.
- [GPT-6 run and original historical comparison](luna-generation-results-2026-09-23.md).
- [Astra-only baseline](three-arm-results-2026-09-22.md).

Offline accounting: `three_arm_analysis.py --root <batch-directory>`.
