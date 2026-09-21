# MiMo-V2.6-Pro comparison

Maintenance evidence only; not loaded during ordinary skill use.

Captured 21 September 2026 from Artificial Analysis's visible comparison tables, Intelligence Index v4.3.2. No graph dataset was downloaded. Rounded display values are retained; do not merge these into the archived 8 September v4.3 rankings.

## Current comparison

Sorted by API-priced benchmark cost per task, lowest first. These are not subscription usage or prices for accepted repository work.

| Configuration | Index | $/task | Terminal-Bench 4.0 | Omniscience index | Output tokens/task (approx.) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MiMo-V2.6-Pro | 46 | $0.13 | 35% | 8 | 64k |
| Luna Max | 37 | $0.18 | 12% | −10 | 41k |
| Sol High | 42 | $0.81 | 21% | 20 | 13k |
| Opus 5 Low | 39 | $1.10 | 26% | 29 | 15k |
| Astra High | 51 | $1.73 | 54% | 44 | 12k |



## Implications

MiMo is a promising bounded implementation candidate: this capture shows a higher coding score and lower benchmark task cost than Luna Max, Sol High and Opus 5 Low. It also emits more output tokens. These measures do not establish real-task savings or justify broadening Kilo's task scope.

Its Omniscience Index is below Sol, Opus and Astra in this comparison. This is a knowledge-reliability index, not a hallucination rate or a measured ability to review code. Keep consequential decisions and acceptance with Codex.

## Runtime

The installed Kilo catalog lists `kilo/xiaomi/mimo-v2.6-pro` as active, with `thinking` (reasoning enabled) and `instant` (reasoning disabled) variants. The default is `thinking`; it matches the reasoning model label, not a proven identical benchmark harness. Kilo catalog rates are $0.435 input, $0.87 output and $0.0036 cached input per million tokens. Kilo 7.7.6 resolved the requested model, variant and step limit for implement, explore and review profiles; the latter two also passed the existing permission checks, without inference. Catalog availability and offline configuration tests do not replace a paid implementation test.

## Evidence

- [Workbook](benchmarks/mimo-model-comparison-2026-09-21.xlsx): comparison and full captured numerical metrics.

- [Visible table capture and Kilo metadata](benchmarks/mimo-comparison-2026-09-21.json): exact displayed strings and capture time.

- [Model page](https://artificialanalysis.ai/models/mimo-v2-6-pro).

- [OpenAI GPT-5.6 Luna (max) comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-gpt-5-6-luna).

- [OpenAI GPT-5.6 Sol (high) comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-gpt-5-6-sol-high).

- [Anthropic Claude Opus 5 (Adaptive Reasoning, Low Effort) comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-claude-opus-5-low).

- [OpenAI GPT-6 Astra (high) comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-gpt-6-astra-high).

