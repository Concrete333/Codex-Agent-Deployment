# GLM-5.3-Flash selection evidence

Maintenance evidence only; not loaded during ordinary deployment.

## Published comparison

Read on 20 September 2026 from Artificial Analysis's public comparison table; no graph dataset was downloaded. The supplied multi-model URL was inaccessible through the web reader. The accessible pairwise page identifies Intelligence Index v4.3.2; do not merge these rounded values into the older workbook as if they were the same capture.

| Metric | GLM-5.3-Flash | Luna Max |
| --- | ---: | ---: |
| Intelligence Index | 42 | 37 |
| Terminal-Bench 4.0 | 33% | 12% |
| SciCode | 52% | 54% |
| AA-LCR v1.1 | 80% | 84% |
| Input / million tokens | $0.15 | $0.20 |
| Output / million tokens | $0.50 | $1.20 |
| Cached input / million tokens | $0.026 | $0.02 |
| Weighted cost / task | $0.25 | $0.18 |
| Output tokens / task | 69k | 41k |

Source: [Artificial Analysis: GLM versus Luna Max](https://artificialanalysis.ai/models/comparisons/glm-5-3-flash-vs-gpt-5-6-luna).

## Selection implications

GLM is a plausible bounded implementation candidate, not a universal Luna replacement. The coding result favors trying it where local implementation judgment matters; retrieval and scientific work do not show the same advantage. Lower token prices coexist with about 68% more output tokens and 39% higher weighted task cost. These are suite measures, not accepted repository-task prices.

The [GLM-5.2 comparison](https://artificialanalysis.ai/models/comparisons/glm-5-3-flash-vs-glm-5-2) also favors Flash on the composite (42 versus 34) and weighted task cost ($0.25 versus $0.96), but does not establish superiority on every task.

## Runtime and acceptance

[Kilo documents GLM-5.3-Flash availability in its CLI](https://blog.kilo.ai/p/ox-alpha-was-glm-53-flash-all-along). Other compatible CLI/provider routes can qualify; this change does not install or validate them. The local Kilo configuration uses `kilo/z-ai/glm-5.3-flash` with no explicit variant.

Earlier personal Kilo smoke tests denied shell/test execution. The implementation profile now preserves normal Kilo tools and configured permissions, allowing worker-owned tests and corrections; explore/review remain restricted. Earlier restricted runs do not validate this revised workflow. Neither a small successful smoke test nor these benchmarks establishes lower total accepted-result cost than Luna in our workflow.

Keep GLM optional, retain verification, and measure worker plus coordinator/checking/repair cost when using it. Codex allowance saved and external-provider spending are separate quantities. No GLM effort ranking or cheaper-reviewer qualification is established here.
