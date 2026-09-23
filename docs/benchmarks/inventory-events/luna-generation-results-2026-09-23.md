# GPT-6 Luna Max versus GPT-5.6 Luna Max

Follow-up: the [same-CLI GPT-5.6 repeat](luna56-repeat-results-2026-09-23.md)
passed without implementation repairs at $0.599674. Against that repeat, GPT-6
worker cost was 52.72% lower and pipeline cost 12.58% lower. The historical
comparison below is retained unchanged.

GPT-6 Luna passed all 27 independent inventory test methods before review.
Astra High accepted it without changing the implementation or worker tests.
The worker cost **59.29% less** than the saved GPT-5.6 Luna run; implementation
plus acceptance cost **23.19% less**.

## Cost and correctness

| Configuration | Worker | Astra High acceptance | Captured total | Worker independent checks |
|---|---:|---:|---:|---|
| GPT-5.6 Luna Max, 22 September | $0.041546 | $0.640958 | $0.682504 | 27/27 |
| GPT-6 Luna Max, 23 September | $0.016914 | $0.507324 | $0.524238 | 27/27 |

Totals use unrounded costs: $0.6825036 and $0.52423786. Both final candidates
also passed all 27 independent methods. One method contains an 80-scenario
lifecycle matrix; these are not 107 independent methods.

The new worker implemented all three modules and added eight tests. Astra added
four acceptance tests, bringing the public/worker/acceptance suite to 16 passing
tests. File comparisons show no changes to Luna's implementation or original
tests during acceptance. Review addressed rollback of existing holds, iterator
exception propagation, strict boolean validation and unbounded quantities.
No additional paid session or correction round occurred.

## Where the saving came from

The worker saved $0.02463174. Astra acceptance saved $0.133634, accounting for
**84.44% of the pipeline's $0.15826574 reduction**. Review still cost **96.77%**
of the new pipeline. This does not establish that changing Luna reliably lowers
review cost, or that a cheaper reviewer can replace Astra without losing accuracy.

| Worker measurement | GPT-5.6 Luna Max | GPT-6 Luna Max |
|---|---:|---:|
| Input, including cache reads | 329,312 | 415,053 |
| Cached input | 281,600 | 361,216 |
| Output, including reasoning | 21,976 | 15,836 |
| Reasoning output, included above | 15,531 | 8,826 |
| Model responses | 13 | 19 |
| Implementation seconds | 1,052.016 | 363.057 |

The new worker generated 27.94% less output and 43.17% less reasoning output,
but processed 26.04% more input and took more model turns. Its lower API rates
also matter: pricing its observed usage at the old Luna rates gives $0.03699492,
about 10.95% below the old worker's cost. That is a price-normalized calculation,
not another observed run or a subscription allowance estimate.

Astra acceptance used 162,706 input tokens (136,704 cached), 2,212 output tokens
(186 reasoning) and eight responses. The old review used 115,937 input
(74,368 cached), 3,018 output (484 reasoning) and six responses. More cached
input and less output helped the new review cost less despite more total input.
Worker plus acceptance elapsed time was 457.60 seconds versus 1,186.30 seconds
previously; concurrent load and service conditions were not controlled.

## Controls and limits

The [protocol](luna-generation-protocol-2026-09-23.md) reused the byte-identical
starter, implementation prompt, result schema, protected files and independent
grader. Acceptance used the same frozen policy snapshot and prompt, with only
its evidence path relocated. The original controls and nine mutants requalified
before inference. All 21 offline runner tests passed. Post-run checks confirmed
the retained driver/prompt/policy/grader fingerprints and protected files.

Effective configurations in native rollouts were `gpt-6-luna/max` and
`gpt-6-astra/high`. Unique per-response usage reconciled to cumulative totals;
neither session recorded cache writes or exceeded the 272k input pricing boundary.
There were no recorded coordination calls. Both stage processes exited zero
without timeout or ownership uncertainty; their PIDs and the supervisor were
absent at inspection. One queued completion message resumed the parent.

The previous executable was no longer installed. The new run used CLI
`0.155.0-alpha.16`; the historical control used `0.155.0-alpha.9.2`. Configuration
was retained, but runtime/system-prompt differences and cache effects remain
confounders. This is one new run against one historical control, not a capability
ranking, repeated average or test of spontaneous delegation decisions.

Costs are API-equivalent estimates using the rates frozen in each manifest,
not bills or quota consumption. Shared preparation, supervision and analysis
are excluded. Pricing sources and rate interpretation are in the protocol.
The clean passes do not qualify a cheaper reviewer or justify dropping checks.

## Retained evidence

`local-luna-generation.json` privately locates batch
`inventory-luna6-d97a3f197ffc4e0cb0cc02bea2800128`. Its `accounting.json` retains
costs, usage, stage timings and worker/acceptance file comparisons; the batch
also retains the frozen manifest, process records, grades and both submissions.

- GPT-6 Luna: `01a0cdbb-6a9f-7571-8157-0678761cb565`.
- Astra acceptance: `01a0cdc0-f70a-7a32-9c63-45ce1a131845`.
- Historical comparison: [22 September results](three-arm-results-2026-09-22.md).

Reproduce the offline accounting with `three_arm_analysis.py --root <batch-directory>`.
No model-routing defaults were changed by this experiment.
