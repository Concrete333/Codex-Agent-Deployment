# GPT and Claude model performance

Evidence snapshot: 8 September 2026. Combined reference prepared 9 September 2026. Maintenance/research only; do not load during operational skill use.

## Sources and reconciliation

22 GPT configurations from the raw chart capture, checked against the corrected GPT workbook, plus 16 configurations from the Claude-only workbook. All source configuration labels, including **with fallback**, are retained. The source is [Artificial Analysis](https://artificialanalysis.ai/models), Intelligence Index v4.3.

- [openai-metrics-raw-2026-09-08.json](benchmarks/openai-metrics-raw-2026-09-08.json) — SHA-256 `df0ea072b3b81d4be010282ce9a9b6e478c30a04f8feeba3c3a3369d3bd53fb0`

- [GPT-model-efficiency-2026-09-08.xlsx](benchmarks/GPT-model-efficiency-2026-09-08.xlsx) — SHA-256 `2f5860223be120d25e8ee6121b03ef8459593a0e6a89aafb6e315080ee9acfc8`

- [claude-model-evidence-2026-09-08.xlsx](benchmarks/claude-model-evidence-2026-09-08.xlsx) — SHA-256 `a023802ec47170f0e1216e5fcf3f759395faddadc1dcad1eae0285ac95006645`


The older `agent-model-selection-2026-09-08.xlsx` is retained as historical material, not used to generate this comparison. Its Task Fit knowledge-reliability row ranks the conditional non-hallucination rate and must not be used as a cross-vendor fabrication ranking. This document recomputes wrong answers on a common denominator and avoids treating composite dominance as a universal task recommendation.

## How to interpret the numbers

- Costs are API-priced benchmark task averages, not Codex/Claude allowance consumption or a quote for repository work. Do not combine subscription percentages into a dollar ranking. Listed token prices are the capture's prices, not a live price feed.
- Output includes reasoning and answer tokens; it excludes input. Per-task averages are weighted across evaluations. Startup context, cache lifetime, reviews, retries, integration and helper calls can change real cost.
- Intelligence Index is a composite, not coding success. Small differences do not establish a reliable winner; the source notes caution against interpreting differences around one point.
- `—` means unavailable, never zero. Six GPT scores are marked estimated. The Claude workbook has no explicit score-status field; do not infer that every pairing was evaluated.
- Claude Fable results explicitly include fallback in the benchmark configuration. Our wrapper does not configure fallback, so those scores are not a measured guarantee for a direct Fable-only worker.
- A cost-frontier flag considers only captured composite score and task cost, across both vendors. It ignores task-specific strengths, uncertainty, permissions, account access and orchestration overhead.
- Wrong answers per question = `(1 - accuracy) × (1 - non-hallucination rate)`. The published non-hallucination rate is conditional on non-correct responses. The derived measure reproduces the captured Omniscience Index via `100 × (accuracy - wrong/question)`. It measures knowledge answers, not source verification or coding defects.
- Percentages below are benchmark scores, not probabilities of success on your assignment.

## Reading the rankings

Each table states its sort metric and direction. Sorts use unrounded source values, with missing measurements last and exact ties ordered by configuration name. Display rounding can hide small differences. Higher benchmark scores and lower costs are favorable on their own metric, not an overall best-to-worst model verdict. Lower token use or shorter duration does not establish equal quality. Frontier calculations also use unrounded values.

## Overall capability

Sorted by Intelligence Index, highest first. Cost and token use are context, not secondary ranking criteria.

| Configuration | Index | Score status | $/task | Output tokens/task | Reasoning share | Combined frontier |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 53.4 | Source score; no status flag | 7.63 | 78,111 | 60.5% | Yes |
| Claude Fable 5.1 (xhigh with fallback) | 53.2 | Source score; no status flag | 5.98 | 60,538 | 56.3% | Yes |
| GPT-6 Astra (max) | 52.8 | Evaluated | 3.26 | 27,206 | 61.4% | Yes |
| GPT-6 Astra (xhigh) | 52.5 | Evaluated | 2.31 | 16,901 | 50.8% | Yes |
| Claude Fable 5.1 (high with fallback) | 51.2 | Source score; no status flag | 3.91 | 38,054 | 48.9% | No |
| GPT-6 Astra (high) | 51.0 | Evaluated | 1.72 | 11,795 | 39.9% | Yes |
| Claude Opus 5 (max) | 50.7 | Source score; no status flag | 5.86 | 72,511 | 59.0% | No |
| Claude Fable 5 (with fallback) | 49.7 | Source score; no status flag | 8.75 | 66,848 | 67.4% | No |
| GPT-6 Astra (medium) | 49.7 | Evaluated | 1.54 | 9,590 | 35.7% | Yes |
| Claude Opus 5 (xhigh) | 49.7 | Source score; no status flag | 4.88 | 60,655 | 57.7% | No |
| Claude Fable 5.1 (medium with fallback) | 49.1 | Source score; no status flag | 2.98 | 27,888 | 43.3% | No |
| Claude Opus 5 (high) | 48.2 | Source score; no status flag | 3.61 | 46,239 | 54.9% | No |
| GPT-5.6 Sol (max) | 47.1 | Evaluated | 1.99 | 29,309 | 59.0% | No |
| Claude Fable 5.1 (low with fallback) | 47.0 | Source score; no status flag | 2.37 | 21,562 | 38.4% | No |
| GPT-6 Astra (low) | 46.0 | Evaluated | 0.82 | 4,433 | 21.2% | Yes |
| GPT-6 Astra (Non-reasoning) | 45.2 | Evaluated | 1.71 | 7,630 | — | No |
| Claude Opus 5 (medium) | 45.1 | Source score; no status flag | 2.19 | 28,977 | 51.3% | No |
| GPT-5.6 Sol (xhigh) | 44.1 | Evaluated | 1.18 | 19,576 | 51.7% | No |
| GPT-5.6 Sol (high) | 42.5 | Evaluated | 0.81 | 13,250 | 44.3% | Yes |
| GPT-5.6 Terra (max) | 42.3 | Evaluated | 1.40 | 38,898 | 67.0% | No |
| Claude Opus 4.8 (max) | 42.0 | Source score; no status flag | 4.08 | 70,550 | 73.4% | No |
| Claude Opus 5 (low) | 39.8 | Source score; no status flag | 1.10 | 14,668 | 44.6% | No |
| GPT-5.6 Sol (medium) | 39.5 | Evaluated | 0.50 | 7,874 | 33.8% | Yes |
| Claude Sonnet 5 (max) | 38.4 | Source score; no status flag | 5.09 | 117,787 | 75.0% | No |
| GPT-5.6 Terra (xhigh) | 38.2 | Evaluated | 0.63 | 20,367 | 56.5% | No |
| GPT-5.6 Luna (max) | 37.5 | Evaluated | 0.18 | 41,235 | 68.1% | Yes |
| GPT-5.6 Luna (xhigh) | 34.8 | Evaluated | 0.09 | 23,624 | 62.3% | Yes |
| GPT-5.6 Terra (high) | 34.5 | Evaluated | 0.34 | 11,294 | 48.2% | No |
| GPT-5.6 Sol (low) | 33.8 | Evaluated | 0.26 | 3,974 | 21.1% | No |
| GPT-5.6 Luna (high) | 32.9 | Estimated | — | — | — | n/a |
| GPT-5.6 Terra (medium) | 32.8 | Estimated | — | — | — | n/a |
| Claude Sonnet 5 (Non-reasoning) | 28.9 | Source score; no status flag | — | — | — | n/a |
| Claude Sonnet 5 (medium) | 28.4 | Source score; no status flag | 1.00 | 27,337 | 56.5% | No |
| GPT-5.6 Terra (low) | 27.9 | Estimated | — | — | — | n/a |
| GPT-5.6 Luna (medium) | 25.8 | Estimated | — | — | — | n/a |
| Claude Sonnet 5 (low) | 24.7 | Source score; no status flag | 0.51 | 15,168 | 46.8% | No |
| GPT-5.6 Terra (Non-reasoning) | 22.3 | Estimated | — | — | — | n/a |
| GPT-5.6 Luna (low) | 21.8 | Estimated | — | — | — | n/a |

## Benchmark task cost

Lowest cost first; this is not cost per accepted repository task.

| Configuration | $/task | Index | Score status |
| --- | --- | --- | --- |
| GPT-5.6 Luna (xhigh) | 0.09 | 34.8 | Evaluated |
| GPT-5.6 Luna (max) | 0.18 | 37.5 | Evaluated |
| GPT-5.6 Sol (low) | 0.26 | 33.8 | Evaluated |
| GPT-5.6 Terra (high) | 0.34 | 34.5 | Evaluated |
| GPT-5.6 Sol (medium) | 0.50 | 39.5 | Evaluated |
| Claude Sonnet 5 (low) | 0.51 | 24.7 | Source score; no status flag |
| GPT-5.6 Terra (xhigh) | 0.63 | 38.2 | Evaluated |
| GPT-5.6 Sol (high) | 0.81 | 42.5 | Evaluated |
| GPT-6 Astra (low) | 0.82 | 46.0 | Evaluated |
| Claude Sonnet 5 (medium) | 1.00 | 28.4 | Source score; no status flag |
| Claude Opus 5 (low) | 1.10 | 39.8 | Source score; no status flag |
| GPT-5.6 Sol (xhigh) | 1.18 | 44.1 | Evaluated |
| GPT-5.6 Terra (max) | 1.40 | 42.3 | Evaluated |
| GPT-6 Astra (medium) | 1.54 | 49.7 | Evaluated |
| GPT-6 Astra (Non-reasoning) | 1.71 | 45.2 | Evaluated |
| GPT-6 Astra (high) | 1.72 | 51.0 | Evaluated |
| GPT-5.6 Sol (max) | 1.99 | 47.1 | Evaluated |
| Claude Opus 5 (medium) | 2.19 | 45.1 | Source score; no status flag |
| GPT-6 Astra (xhigh) | 2.31 | 52.5 | Evaluated |
| Claude Fable 5.1 (low with fallback) | 2.37 | 47.0 | Source score; no status flag |
| Claude Fable 5.1 (medium with fallback) | 2.98 | 49.1 | Source score; no status flag |
| GPT-6 Astra (max) | 3.26 | 52.8 | Evaluated |
| Claude Opus 5 (high) | 3.61 | 48.2 | Source score; no status flag |
| Claude Fable 5.1 (high with fallback) | 3.91 | 51.2 | Source score; no status flag |
| Claude Opus 4.8 (max) | 4.08 | 42.0 | Source score; no status flag |
| Claude Opus 5 (xhigh) | 4.88 | 49.7 | Source score; no status flag |
| Claude Sonnet 5 (max) | 5.09 | 38.4 | Source score; no status flag |
| Claude Opus 5 (max) | 5.86 | 50.7 | Source score; no status flag |
| Claude Fable 5.1 (xhigh with fallback) | 5.98 | 53.2 | Source score; no status flag |
| Claude Fable 5.1 (max with fallback) | 7.63 | 53.4 | Source score; no status flag |
| Claude Fable 5 (with fallback) | 8.75 | 49.7 | Source score; no status flag |
| Claude Sonnet 5 (Non-reasoning) | — | 28.9 | Source score; no status flag |
| GPT-5.6 Luna (high) | — | 32.9 | Estimated |
| GPT-5.6 Luna (low) | — | 21.8 | Estimated |
| GPT-5.6 Luna (medium) | — | 25.8 | Estimated |
| GPT-5.6 Terra (Non-reasoning) | — | 22.3 | Estimated |
| GPT-5.6 Terra (low) | — | 27.9 | Estimated |
| GPT-5.6 Terra (medium) | — | 32.8 | Estimated |

## Output-token use

Fewest output tokens first, including reasoning. This is token volume, not capability-adjusted efficiency.

| Configuration | Output tokens/task | Index | Score status |
| --- | --- | --- | --- |
| GPT-5.6 Sol (low) | 3,974 | 33.8 | Evaluated |
| GPT-6 Astra (low) | 4,433 | 46.0 | Evaluated |
| GPT-6 Astra (Non-reasoning) | 7,630 | 45.2 | Evaluated |
| GPT-5.6 Sol (medium) | 7,874 | 39.5 | Evaluated |
| GPT-6 Astra (medium) | 9,590 | 49.7 | Evaluated |
| GPT-5.6 Terra (high) | 11,294 | 34.5 | Evaluated |
| GPT-6 Astra (high) | 11,795 | 51.0 | Evaluated |
| GPT-5.6 Sol (high) | 13,250 | 42.5 | Evaluated |
| Claude Opus 5 (low) | 14,668 | 39.8 | Source score; no status flag |
| Claude Sonnet 5 (low) | 15,168 | 24.7 | Source score; no status flag |
| GPT-6 Astra (xhigh) | 16,901 | 52.5 | Evaluated |
| GPT-5.6 Sol (xhigh) | 19,576 | 44.1 | Evaluated |
| GPT-5.6 Terra (xhigh) | 20,367 | 38.2 | Evaluated |
| Claude Fable 5.1 (low with fallback) | 21,562 | 47.0 | Source score; no status flag |
| GPT-5.6 Luna (xhigh) | 23,624 | 34.8 | Evaluated |
| GPT-6 Astra (max) | 27,206 | 52.8 | Evaluated |
| Claude Sonnet 5 (medium) | 27,337 | 28.4 | Source score; no status flag |
| Claude Fable 5.1 (medium with fallback) | 27,888 | 49.1 | Source score; no status flag |
| Claude Opus 5 (medium) | 28,977 | 45.1 | Source score; no status flag |
| GPT-5.6 Sol (max) | 29,309 | 47.1 | Evaluated |
| Claude Fable 5.1 (high with fallback) | 38,054 | 51.2 | Source score; no status flag |
| GPT-5.6 Terra (max) | 38,898 | 42.3 | Evaluated |
| GPT-5.6 Luna (max) | 41,235 | 37.5 | Evaluated |
| Claude Opus 5 (high) | 46,239 | 48.2 | Source score; no status flag |
| Claude Fable 5.1 (xhigh with fallback) | 60,538 | 53.2 | Source score; no status flag |
| Claude Opus 5 (xhigh) | 60,655 | 49.7 | Source score; no status flag |
| Claude Fable 5 (with fallback) | 66,848 | 49.7 | Source score; no status flag |
| Claude Opus 4.8 (max) | 70,550 | 42.0 | Source score; no status flag |
| Claude Opus 5 (max) | 72,511 | 50.7 | Source score; no status flag |
| Claude Fable 5.1 (max with fallback) | 78,111 | 53.4 | Source score; no status flag |
| Claude Sonnet 5 (max) | 117,787 | 38.4 | Source score; no status flag |
| Claude Sonnet 5 (Non-reasoning) | — | 28.9 | Source score; no status flag |
| GPT-5.6 Luna (high) | — | 32.9 | Estimated |
| GPT-5.6 Luna (low) | — | 21.8 | Estimated |
| GPT-5.6 Luna (medium) | — | 25.8 | Estimated |
| GPT-5.6 Terra (Non-reasoning) | — | 22.3 | Estimated |
| GPT-5.6 Terra (low) | — | 27.9 | Estimated |
| GPT-5.6 Terra (medium) | — | 32.8 | Estimated |

## Benchmark duration

Shortest duration first. Elapsed time is not a routing priority.

| Configuration | Minutes/task | Index | Score status |
| --- | --- | --- | --- |
| GPT-5.6 Sol (low) | 0.99 | 33.8 | Evaluated |
| GPT-6 Astra (low) | 1.41 | 46.0 | Evaluated |
| GPT-5.6 Terra (high) | 1.92 | 34.5 | Evaluated |
| GPT-5.6 Sol (medium) | 1.93 | 39.5 | Evaluated |
| Claude Sonnet 5 (low) | 2.36 | 24.7 | Source score; no status flag |
| Claude Opus 5 (low) | 2.77 | 39.8 | Source score; no status flag |
| GPT-6 Astra (medium) | 2.96 | 49.7 | Evaluated |
| GPT-5.6 Sol (high) | 3.26 | 42.5 | Evaluated |
| GPT-5.6 Terra (xhigh) | 3.39 | 38.2 | Evaluated |
| GPT-5.6 Luna (xhigh) | 3.53 | 34.8 | Evaluated |
| GPT-6 Astra (high) | 3.56 | 51.0 | Evaluated |
| Claude Fable 5.1 (low with fallback) | 4.06 | 47.0 | Source score; no status flag |
| Claude Sonnet 5 (medium) | 4.14 | 28.4 | Source score; no status flag |
| GPT-5.6 Sol (xhigh) | 4.92 | 44.1 | Evaluated |
| GPT-6 Astra (xhigh) | 5.01 | 52.5 | Evaluated |
| Claude Fable 5.1 (medium with fallback) | 5.16 | 49.1 | Source score; no status flag |
| Claude Opus 5 (medium) | 5.37 | 45.1 | Source score; no status flag |
| GPT-5.6 Terra (max) | 5.61 | 42.3 | Evaluated |
| GPT-5.6 Luna (max) | 5.64 | 37.5 | Evaluated |
| GPT-5.6 Sol (max) | 6.82 | 47.1 | Evaluated |
| Claude Fable 5.1 (high with fallback) | 6.98 | 51.2 | Source score; no status flag |
| GPT-6 Astra (max) | 7.79 | 52.8 | Evaluated |
| Claude Opus 5 (high) | 8.72 | 48.2 | Source score; no status flag |
| Claude Fable 5 (with fallback) | 10.06 | 49.7 | Source score; no status flag |
| Claude Fable 5.1 (xhigh with fallback) | 10.32 | 53.2 | Source score; no status flag |
| Claude Opus 4.8 (max) | 11.99 | 42.0 | Source score; no status flag |
| Claude Opus 5 (xhigh) | 12.00 | 49.7 | Source score; no status flag |
| Claude Fable 5.1 (max with fallback) | 12.07 | 53.4 | Source score; no status flag |
| Claude Opus 5 (max) | 13.18 | 50.7 | Source score; no status flag |
| Claude Sonnet 5 (max) | 15.14 | 38.4 | Source score; no status flag |
| Claude Sonnet 5 (Non-reasoning) | — | 28.9 | Source score; no status flag |
| GPT-5.6 Luna (high) | — | 32.9 | Estimated |
| GPT-5.6 Luna (low) | — | 21.8 | Estimated |
| GPT-5.6 Luna (medium) | — | 25.8 | Estimated |
| GPT-5.6 Terra (Non-reasoning) | — | 22.3 | Estimated |
| GPT-5.6 Terra (low) | — | 27.9 | Estimated |
| GPT-5.6 Terra (medium) | — | 32.8 | Estimated |
| GPT-6 Astra (Non-reasoning) | — | 45.2 | Evaluated |

## Coding, long-context and knowledge rankings

Each metric has its own descending ranking. Scores are shown as percentages with six decimal places to retain the precision of the full evaluation tables. The composite score-status flag does not establish whether each individual evaluation was measured.

### Terminal-Bench v4.0

Highest score first.

| Configuration | Terminal-Bench v4.0 | $/task |
| --- | --- | --- |
| GPT-6 Astra (xhigh) | 59.595960% | 2.31 |
| GPT-6 Astra (max) | 59.090909% | 3.26 |
| Claude Fable 5.1 (xhigh with fallback) | 55.050505% | 5.98 |
| GPT-6 Astra (high) | 54.040404% | 1.72 |
| Claude Fable 5.1 (high with fallback) | 52.020202% | 3.91 |
| Claude Fable 5.1 (max with fallback) | 52.020202% | 7.63 |
| GPT-6 Astra (Non-reasoning) | 50.505051% | 1.71 |
| GPT-6 Astra (medium) | 49.494949% | 1.54 |
| Claude Opus 5 (max) | 48.989899% | 5.86 |
| Claude Opus 5 (xhigh) | 46.464646% | 4.88 |
| Claude Opus 5 (high) | 45.959596% | 3.61 |
| Claude Fable 5.1 (medium with fallback) | 44.949495% | 2.98 |
| Claude Fable 5 (with fallback) | 42.424242% | 8.75 |
| GPT-6 Astra (low) | 41.919192% | 0.82 |
| Claude Fable 5.1 (low with fallback) | 40.404040% | 2.37 |
| GPT-5.6 Sol (max) | 39.898990% | 1.99 |
| GPT-5.6 Terra (max) | 35.353535% | 1.40 |
| Claude Opus 5 (medium) | 34.343434% | 2.19 |
| Claude Opus 5 (low) | 26.262626% | 1.10 |
| GPT-5.6 Sol (xhigh) | 24.747475% | 1.18 |
| Claude Opus 4.8 (max) | 21.717172% | 4.08 |
| GPT-5.6 Sol (high) | 20.707071% | 0.81 |
| GPT-5.6 Sol (medium) | 14.646465% | 0.50 |
| Claude Sonnet 5 (max) | 14.141414% | 5.09 |
| GPT-5.6 Luna (max) | 11.616162% | 0.18 |
| GPT-5.6 Terra (xhigh) | 10.101010% | 0.63 |
| GPT-5.6 Luna (xhigh) | 3.535354% | 0.09 |
| Claude Sonnet 5 (low) | 2.525253% | 0.51 |
| GPT-5.6 Luna (high) | 2.525253% | — |
| Claude Sonnet 5 (medium) | 2.020202% | 1.00 |
| GPT-5.6 Terra (high) | 1.515152% | 0.34 |
| GPT-5.6 Terra (low) | 1.515152% | — |
| GPT-5.6 Sol (low) | 1.010101% | 0.26 |
| GPT-5.6 Terra (medium) | 1.010101% | — |
| GPT-5.6 Luna (medium) | 0.505051% | — |
| GPT-5.6 Luna (low) | 0.000000% | — |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| GPT-5.6 Terra (Non-reasoning) | — | — |

### SciCode

Highest score first.

| Configuration | SciCode | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 63.078704% | 7.63 |
| Claude Fable 5 (with fallback) | 60.995370% | 8.75 |
| Claude Fable 5.1 (xhigh with fallback) | 60.879630% | 5.98 |
| Claude Fable 5.1 (high with fallback) | 58.680556% | 3.91 |
| GPT-5.6 Sol (high) | 57.754630% | 0.81 |
| GPT-5.6 Sol (medium) | 57.407407% | 0.50 |
| GPT-5.6 Sol (max) | 57.060185% | 1.99 |
| GPT-5.6 Sol (xhigh) | 57.060185% | 1.18 |
| Claude Fable 5.1 (low with fallback) | 56.712963% | 2.37 |
| GPT-6 Astra (max) | 56.481481% | 3.26 |
| Claude Fable 5.1 (medium with fallback) | 56.365741% | 2.98 |
| Claude Opus 5 (max) | 56.365741% | 5.86 |
| GPT-5.6 Sol (low) | 56.365741% | 0.26 |
| Claude Opus 5 (xhigh) | 55.671296% | 4.88 |
| GPT-6 Astra (xhigh) | 55.671296% | 2.31 |
| Claude Opus 5 (high) | 55.439815% | 3.61 |
| GPT-6 Astra (high) | 55.439815% | 1.72 |
| GPT-5.6 Terra (max) | 54.976852% | 1.40 |
| Claude Opus 4.8 (max) | 54.398148% | 4.08 |
| Claude Sonnet 5 (max) | 54.282407% | 5.09 |
| GPT-6 Astra (medium) | 54.166667% | 1.54 |
| GPT-6 Astra (low) | 54.050926% | 0.82 |
| GPT-5.6 Luna (max) | 53.587963% | 0.18 |
| GPT-6 Astra (Non-reasoning) | 53.472222% | 1.71 |
| GPT-5.6 Terra (high) | 52.430556% | 0.34 |
| GPT-5.6 Terra (xhigh) | 52.314815% | 0.63 |
| Claude Sonnet 5 (medium) | 51.620370% | 1.00 |
| GPT-5.6 Luna (high) | 51.620370% | — |
| Claude Opus 5 (medium) | 51.504630% | 2.19 |
| GPT-5.6 Luna (xhigh) | 50.462963% | 0.09 |
| GPT-5.6 Terra (medium) | 50.462963% | — |
| Claude Sonnet 5 (low) | 50.115741% | 0.51 |
| GPT-5.6 Terra (low) | 49.884259% | — |
| Claude Opus 5 (low) | 49.189815% | 1.10 |
| GPT-5.6 Luna (medium) | 46.759259% | — |
| GPT-5.6 Luna (low) | 46.064815% | — |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| GPT-5.6 Terra (Non-reasoning) | — | — |

### AA-LCR v1.1

Highest score first.

| Configuration | AA-LCR v1.1 | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 85.333333% | 7.63 |
| Claude Fable 5.1 (medium with fallback) | 84.666667% | 2.98 |
| GPT-5.6 Sol (max) | 84.000000% | 1.99 |
| Claude Fable 5.1 (high with fallback) | 83.666667% | 3.91 |
| GPT-5.6 Luna (max) | 83.666667% | 0.18 |
| Claude Fable 5.1 (xhigh with fallback) | 83.000000% | 5.98 |
| GPT-5.6 Terra (max) | 83.000000% | 1.40 |
| Claude Fable 5 (with fallback) | 82.333333% | 8.75 |
| Claude Fable 5.1 (low with fallback) | 82.333333% | 2.37 |
| GPT-5.6 Sol (xhigh) | 82.333333% | 1.18 |
| Claude Opus 5 (medium) | 82.000000% | 2.19 |
| Claude Sonnet 5 (max) | 82.000000% | 5.09 |
| GPT-5.6 Luna (xhigh) | 81.666667% | 0.09 |
| GPT-5.6 Sol (high) | 81.666667% | 0.81 |
| Claude Opus 5 (low) | 81.333333% | 1.10 |
| GPT-6 Astra (max) | 80.666667% | 3.26 |
| Claude Opus 5 (xhigh) | 80.333333% | 4.88 |
| GPT-5.6 Luna (high) | 80.333333% | — |
| GPT-5.6 Sol (medium) | 80.333333% | 0.50 |
| GPT-6 Astra (high) | 80.000000% | 1.72 |
| GPT-6 Astra (low) | 80.000000% | 0.82 |
| GPT-6 Astra (xhigh) | 80.000000% | 2.31 |
| GPT-6 Astra (medium) | 79.666667% | 1.54 |
| Claude Opus 5 (max) | 79.333333% | 5.86 |
| Claude Opus 5 (high) | 79.000000% | 3.61 |
| GPT-5.6 Terra (xhigh) | 79.000000% | 0.63 |
| GPT-5.6 Sol (low) | 78.000000% | 0.26 |
| Claude Opus 4.8 (max) | 77.666667% | 4.08 |
| GPT-5.6 Terra (high) | 77.666667% | 0.34 |
| GPT-5.6 Luna (medium) | 75.000000% | — |
| GPT-5.6 Terra (medium) | 74.000000% | — |
| Claude Sonnet 5 (medium) | 73.666667% | 1.00 |
| GPT-5.6 Terra (low) | 71.333333% | — |
| GPT-6 Astra (Non-reasoning) | 70.666667% | 1.71 |
| Claude Sonnet 5 (Non-reasoning) | 70.000000% | — |
| GPT-5.6 Luna (low) | 70.000000% | — |
| Claude Sonnet 5 (low) | 67.333333% | 0.51 |
| GPT-5.6 Terra (Non-reasoning) | 58.666667% | — |

### AA-Omniscience Accuracy

Highest score first.

| Configuration | AA-Omniscience Accuracy | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 67.233333% | 7.63 |
| Claude Fable 5.1 (xhigh with fallback) | 66.216667% | 5.98 |
| Claude Fable 5 (with fallback) | 65.350000% | 8.75 |
| Claude Fable 5.1 (high with fallback) | 64.933333% | 3.91 |
| Claude Fable 5.1 (medium with fallback) | 63.100000% | 2.98 |
| GPT-6 Astra (max) | 62.600000% | 3.26 |
| GPT-6 Astra (xhigh) | 61.850000% | 2.31 |
| GPT-6 Astra (high) | 61.133333% | 1.72 |
| Claude Opus 5 (max) | 60.866667% | 5.86 |
| GPT-6 Astra (medium) | 60.566667% | 1.54 |
| Claude Fable 5.1 (low with fallback) | 60.233333% | 2.37 |
| GPT-6 Astra (low) | 59.533333% | 0.82 |
| Claude Opus 5 (xhigh) | 59.500000% | 4.88 |
| GPT-5.6 Sol (max) | 59.400000% | 1.99 |
| Claude Opus 5 (high) | 58.883333% | 3.61 |
| GPT-5.6 Sol (xhigh) | 58.816667% | 1.18 |
| GPT-5.6 Sol (high) | 58.350000% | 0.81 |
| GPT-5.6 Sol (medium) | 57.750000% | 0.50 |
| GPT-5.6 Sol (low) | 57.166667% | 0.26 |
| Claude Opus 5 (medium) | 57.066667% | 2.19 |
| Claude Opus 5 (low) | 55.950000% | 1.10 |
| GPT-6 Astra (Non-reasoning) | 55.600000% | 1.71 |
| Claude Opus 4.8 (max) | 48.833333% | 4.08 |
| GPT-5.6 Terra (max) | 46.800000% | 1.40 |
| GPT-5.6 Terra (xhigh) | 45.516667% | 0.63 |
| GPT-5.6 Terra (high) | 45.483333% | 0.34 |
| GPT-5.6 Terra (medium) | 44.600000% | — |
| GPT-5.6 Terra (low) | 43.733333% | — |
| GPT-5.6 Luna (max) | 42.733333% | 0.18 |
| GPT-5.6 Luna (xhigh) | 42.450000% | 0.09 |
| GPT-5.6 Luna (high) | 41.783333% | — |
| GPT-5.6 Luna (medium) | 40.700000% | — |
| Claude Sonnet 5 (max) | 40.050000% | 5.09 |
| GPT-5.6 Luna (low) | 39.616667% | — |
| Claude Sonnet 5 (low) | 37.350000% | 0.51 |
| Claude Sonnet 5 (medium) | 37.100000% | 1.00 |
| GPT-5.6 Terra (Non-reasoning) | 36.816667% | — |
| Claude Sonnet 5 (Non-reasoning) | 33.800000% | — |

### Wrong answers per question

Lowest wrong-answer share first. Accuracy is shown alongside it: declining more questions is not the same as answering more correctly.

| Configuration | Wrong/question | Knowledge accuracy | $/task |
| --- | --- | --- | --- |
| GPT-6 Astra (high) | 17.400% | 61.133% | 1.72 |
| GPT-6 Astra (medium) | 18.350% | 60.567% | 1.54 |
| GPT-6 Astra (xhigh) | 18.433% | 61.850% | 2.31 |
| GPT-6 Astra (low) | 18.983% | 59.533% | 0.82 |
| GPT-6 Astra (max) | 19.200% | 62.600% | 3.26 |
| Claude Opus 4.8 (max) | 20.083% | 48.833% | 4.08 |
| Claude Fable 5 (with fallback) | 22.050% | 65.350% | 8.75 |
| Claude Sonnet 5 (max) | 23.600% | 40.050% | 5.09 |
| Claude Fable 5.1 (max with fallback) | 23.783% | 67.233% | 7.63 |
| Claude Opus 5 (max) | 23.800% | 60.867% | 5.86 |
| Claude Fable 5.1 (xhigh with fallback) | 23.833% | 66.217% | 5.98 |
| Claude Opus 5 (xhigh) | 24.117% | 59.500% | 4.88 |
| Claude Fable 5.1 (high with fallback) | 24.133% | 64.933% | 3.91 |
| Claude Opus 5 (high) | 25.167% | 58.883% | 3.61 |
| Claude Fable 5.1 (medium with fallback) | 25.500% | 63.100% | 2.98 |
| Claude Opus 5 (medium) | 26.050% | 57.067% | 2.19 |
| Claude Fable 5.1 (low with fallback) | 26.100% | 60.233% | 2.37 |
| Claude Opus 5 (low) | 27.400% | 55.950% | 1.10 |
| GPT-6 Astra (Non-reasoning) | 29.050% | 55.600% | 1.71 |
| Claude Sonnet 5 (Non-reasoning) | 34.450% | 33.800% | — |
| GPT-5.6 Sol (max) | 37.433% | 59.400% | 1.99 |
| GPT-5.6 Sol (xhigh) | 37.833% | 58.817% | 1.18 |
| GPT-5.6 Sol (high) | 37.983% | 58.350% | 0.81 |
| GPT-5.6 Sol (low) | 38.300% | 57.167% | 0.26 |
| GPT-5.6 Sol (medium) | 38.350% | 57.750% | 0.50 |
| Claude Sonnet 5 (medium) | 43.967% | 37.100% | 1.00 |
| Claude Sonnet 5 (low) | 45.583% | 37.350% | 0.51 |
| GPT-5.6 Terra (max) | 46.750% | 46.800% | 1.40 |
| GPT-5.6 Terra (xhigh) | 48.500% | 45.517% | 0.63 |
| GPT-5.6 Terra (high) | 48.950% | 45.483% | 0.34 |
| GPT-5.6 Terra (medium) | 49.733% | 44.600% | — |
| GPT-5.6 Terra (low) | 50.567% | 43.733% | — |
| GPT-5.6 Luna (max) | 53.017% | 42.733% | 0.18 |
| GPT-5.6 Luna (xhigh) | 53.217% | 42.450% | 0.09 |
| GPT-5.6 Luna (high) | 53.783% | 41.783% | — |
| GPT-5.6 Luna (medium) | 53.883% | 40.700% | — |
| GPT-5.6 Luna (low) | 54.267% | 39.617% | — |
| GPT-5.6 Terra (Non-reasoning) | 60.033% | 36.817% | — |

## Captured API token rates

Each rate is ranked separately, lowest first, in USD per million tokens. A cheaper input rate need not mean a cheaper complete task. Context is the captured AA field, not an account/runtime entitlement. Expand a rate to see all configurations.

<details>
<summary>Input $/M — lowest first</summary>

| Configuration | Input $/M | Context tokens |
| --- | --- | --- |
| GPT-5.6 Luna (high) | 0.20 | 1,000,000 |
| GPT-5.6 Luna (low) | 0.20 | 1,000,000 |
| GPT-5.6 Luna (max) | 0.20 | 1,000,000 |
| GPT-5.6 Luna (medium) | 0.20 | 1,000,000 |
| GPT-5.6 Luna (xhigh) | 0.20 | 1,000,000 |
| Claude Sonnet 5 (Non-reasoning) | 2.00 | 1,000,000 |
| Claude Sonnet 5 (low) | 2.00 | 1,000,000 |
| Claude Sonnet 5 (max) | 2.00 | 1,000,000 |
| Claude Sonnet 5 (medium) | 2.00 | 1,000,000 |
| GPT-5.6 Terra (Non-reasoning) | 2.00 | 1,000,000 |
| GPT-5.6 Terra (high) | 2.00 | 1,000,000 |
| GPT-5.6 Terra (low) | 2.00 | 1,000,000 |
| GPT-5.6 Terra (max) | 2.00 | 1,000,000 |
| GPT-5.6 Terra (medium) | 2.00 | 1,000,000 |
| GPT-5.6 Terra (xhigh) | 2.00 | 1,000,000 |
| GPT-5.6 Sol (high) | 4.00 | 1,000,000 |
| GPT-5.6 Sol (low) | 4.00 | 1,000,000 |
| GPT-5.6 Sol (max) | 4.00 | 1,000,000 |
| GPT-5.6 Sol (medium) | 4.00 | 1,000,000 |
| GPT-5.6 Sol (xhigh) | 4.00 | 1,000,000 |
| Claude Opus 4.8 (max) | 5.00 | 1,000,000 |
| Claude Opus 5 (high) | 5.00 | 1,000,000 |
| Claude Opus 5 (low) | 5.00 | 1,000,000 |
| Claude Opus 5 (max) | 5.00 | 1,000,000 |
| Claude Opus 5 (medium) | 5.00 | 1,000,000 |
| Claude Opus 5 (xhigh) | 5.00 | 1,000,000 |
| Claude Fable 5 (with fallback) | 10.00 | 1,000,000 |
| Claude Fable 5.1 (high with fallback) | 10.00 | 1,000,000 |
| Claude Fable 5.1 (low with fallback) | 10.00 | 1,000,000 |
| Claude Fable 5.1 (max with fallback) | 10.00 | 1,000,000 |
| Claude Fable 5.1 (medium with fallback) | 10.00 | 1,000,000 |
| Claude Fable 5.1 (xhigh with fallback) | 10.00 | 1,000,000 |
| GPT-6 Astra (Non-reasoning) | 10.00 | 1,000,000 |
| GPT-6 Astra (high) | 10.00 | 1,000,000 |
| GPT-6 Astra (low) | 10.00 | 1,000,000 |
| GPT-6 Astra (max) | 10.00 | 1,000,000 |
| GPT-6 Astra (medium) | 10.00 | 1,000,000 |
| GPT-6 Astra (xhigh) | 10.00 | 1,000,000 |

</details>

<details>
<summary>Output $/M — lowest first</summary>

| Configuration | Output $/M | Context tokens |
| --- | --- | --- |
| GPT-5.6 Luna (high) | 1.20 | 1,000,000 |
| GPT-5.6 Luna (low) | 1.20 | 1,000,000 |
| GPT-5.6 Luna (max) | 1.20 | 1,000,000 |
| GPT-5.6 Luna (medium) | 1.20 | 1,000,000 |
| GPT-5.6 Luna (xhigh) | 1.20 | 1,000,000 |
| Claude Sonnet 5 (Non-reasoning) | 10.00 | 1,000,000 |
| Claude Sonnet 5 (low) | 10.00 | 1,000,000 |
| Claude Sonnet 5 (max) | 10.00 | 1,000,000 |
| Claude Sonnet 5 (medium) | 10.00 | 1,000,000 |
| GPT-5.6 Terra (Non-reasoning) | 12.00 | 1,000,000 |
| GPT-5.6 Terra (high) | 12.00 | 1,000,000 |
| GPT-5.6 Terra (low) | 12.00 | 1,000,000 |
| GPT-5.6 Terra (max) | 12.00 | 1,000,000 |
| GPT-5.6 Terra (medium) | 12.00 | 1,000,000 |
| GPT-5.6 Terra (xhigh) | 12.00 | 1,000,000 |
| GPT-5.6 Sol (high) | 20.00 | 1,000,000 |
| GPT-5.6 Sol (low) | 20.00 | 1,000,000 |
| GPT-5.6 Sol (max) | 20.00 | 1,000,000 |
| GPT-5.6 Sol (medium) | 20.00 | 1,000,000 |
| GPT-5.6 Sol (xhigh) | 20.00 | 1,000,000 |
| Claude Opus 4.8 (max) | 25.00 | 1,000,000 |
| Claude Opus 5 (high) | 25.00 | 1,000,000 |
| Claude Opus 5 (low) | 25.00 | 1,000,000 |
| Claude Opus 5 (max) | 25.00 | 1,000,000 |
| Claude Opus 5 (medium) | 25.00 | 1,000,000 |
| Claude Opus 5 (xhigh) | 25.00 | 1,000,000 |
| Claude Fable 5 (with fallback) | 50.00 | 1,000,000 |
| Claude Fable 5.1 (high with fallback) | 50.00 | 1,000,000 |
| Claude Fable 5.1 (low with fallback) | 50.00 | 1,000,000 |
| Claude Fable 5.1 (max with fallback) | 50.00 | 1,000,000 |
| Claude Fable 5.1 (medium with fallback) | 50.00 | 1,000,000 |
| Claude Fable 5.1 (xhigh with fallback) | 50.00 | 1,000,000 |
| GPT-6 Astra (Non-reasoning) | 50.00 | 1,000,000 |
| GPT-6 Astra (high) | 50.00 | 1,000,000 |
| GPT-6 Astra (low) | 50.00 | 1,000,000 |
| GPT-6 Astra (max) | 50.00 | 1,000,000 |
| GPT-6 Astra (medium) | 50.00 | 1,000,000 |
| GPT-6 Astra (xhigh) | 50.00 | 1,000,000 |

</details>

<details>
<summary>Cache-hit $/M — lowest first</summary>

| Configuration | Cache-hit $/M | Context tokens |
| --- | --- | --- |
| GPT-5.6 Luna (high) | 0.02 | 1,000,000 |
| GPT-5.6 Luna (low) | 0.02 | 1,000,000 |
| GPT-5.6 Luna (max) | 0.02 | 1,000,000 |
| GPT-5.6 Luna (medium) | 0.02 | 1,000,000 |
| GPT-5.6 Luna (xhigh) | 0.02 | 1,000,000 |
| Claude Sonnet 5 (Non-reasoning) | 0.20 | 1,000,000 |
| Claude Sonnet 5 (low) | 0.20 | 1,000,000 |
| Claude Sonnet 5 (max) | 0.20 | 1,000,000 |
| Claude Sonnet 5 (medium) | 0.20 | 1,000,000 |
| GPT-5.6 Terra (Non-reasoning) | 0.20 | 1,000,000 |
| GPT-5.6 Terra (high) | 0.20 | 1,000,000 |
| GPT-5.6 Terra (low) | 0.20 | 1,000,000 |
| GPT-5.6 Terra (max) | 0.20 | 1,000,000 |
| GPT-5.6 Terra (medium) | 0.20 | 1,000,000 |
| GPT-5.6 Terra (xhigh) | 0.20 | 1,000,000 |
| Claude Fable 5.1 (high with fallback) | 0.25 | 1,000,000 |
| Claude Fable 5.1 (low with fallback) | 0.25 | 1,000,000 |
| Claude Fable 5.1 (max with fallback) | 0.25 | 1,000,000 |
| Claude Fable 5.1 (medium with fallback) | 0.25 | 1,000,000 |
| Claude Fable 5.1 (xhigh with fallback) | 0.25 | 1,000,000 |
| GPT-5.6 Sol (high) | 0.40 | 1,000,000 |
| GPT-5.6 Sol (low) | 0.40 | 1,000,000 |
| GPT-5.6 Sol (max) | 0.40 | 1,000,000 |
| GPT-5.6 Sol (medium) | 0.40 | 1,000,000 |
| GPT-5.6 Sol (xhigh) | 0.40 | 1,000,000 |
| Claude Opus 4.8 (max) | 0.50 | 1,000,000 |
| Claude Opus 5 (high) | 0.50 | 1,000,000 |
| Claude Opus 5 (low) | 0.50 | 1,000,000 |
| Claude Opus 5 (max) | 0.50 | 1,000,000 |
| Claude Opus 5 (medium) | 0.50 | 1,000,000 |
| Claude Opus 5 (xhigh) | 0.50 | 1,000,000 |
| Claude Fable 5 (with fallback) | 1.00 | 1,000,000 |
| GPT-6 Astra (Non-reasoning) | 1.00 | 1,000,000 |
| GPT-6 Astra (high) | 1.00 | 1,000,000 |
| GPT-6 Astra (low) | 1.00 | 1,000,000 |
| GPT-6 Astra (max) | 1.00 | 1,000,000 |
| GPT-6 Astra (medium) | 1.00 | 1,000,000 |
| GPT-6 Astra (xhigh) | 1.00 | 1,000,000 |

</details>

## Other evaluation rankings

Expand a metric for its highest-to-lowest ranking. Scores retain source units (mostly fractions) to six decimal places. The four featured evaluations above are not repeated here.

<details>
<summary>AA-Briefcase — highest first</summary>

| Configuration | AA-Briefcase | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 0.580910 | 7.63 |
| Claude Fable 5.1 (xhigh with fallback) | 0.575005 | 5.98 |
| Claude Opus 5 (max) | 0.572450 | 5.86 |
| Claude Opus 5 (xhigh) | 0.562280 | 4.88 |
| Claude Fable 5.1 (high with fallback) | 0.539095 | 3.91 |
| GPT-6 Astra (max) | 0.531005 | 3.26 |
| Claude Opus 5 (high) | 0.528330 | 3.61 |
| GPT-6 Astra (xhigh) | 0.516865 | 2.31 |
| Claude Fable 5.1 (medium with fallback) | 0.515600 | 2.98 |
| Claude Fable 5 (with fallback) | 0.514810 | 8.75 |
| GPT-6 Astra (high) | 0.496935 | 1.72 |
| Claude Fable 5.1 (low with fallback) | 0.491865 | 2.37 |
| GPT-5.6 Sol (max) | 0.487500 | 1.99 |
| GPT-6 Astra (Non-reasoning) | 0.485660 | 1.71 |
| GPT-6 Astra (medium) | 0.475300 | 1.54 |
| Claude Opus 5 (medium) | 0.469520 | 2.19 |
| GPT-5.6 Sol (xhigh) | 0.467340 | 1.18 |
| GPT-5.6 Sol (high) | 0.430440 | 0.81 |
| Claude Sonnet 5 (max) | 0.427595 | 5.09 |
| GPT-5.6 Luna (max) | 0.419690 | 0.18 |
| GPT-5.6 Terra (xhigh) | 0.418640 | 0.63 |
| GPT-5.6 Terra (max) | 0.415000 | 1.40 |
| Claude Opus 4.8 (max) | 0.407975 | 4.08 |
| GPT-5.6 Luna (xhigh) | 0.384005 | 0.09 |
| GPT-6 Astra (low) | 0.376550 | 0.82 |
| GPT-5.6 Sol (medium) | 0.370180 | 0.50 |
| Claude Opus 5 (low) | 0.357865 | 1.10 |
| GPT-5.6 Terra (high) | 0.350680 | 0.34 |
| GPT-5.6 Luna (high) | 0.336420 | — |
| Claude Sonnet 5 (medium) | 0.276940 | 1.00 |
| GPT-5.6 Sol (low) | 0.271030 | 0.26 |
| GPT-5.6 Terra (medium) | 0.270570 | — |
| GPT-5.6 Terra (low) | 0.257090 | — |
| GPT-5.6 Terra (Non-reasoning) | 0.223345 | — |
| GPT-5.6 Luna (medium) | 0.216685 | — |
| Claude Sonnet 5 (low) | 0.213705 | 0.51 |
| GPT-5.6 Luna (low) | 0.121020 | — |
| Claude Sonnet 5 (Non-reasoning) | — | — |

</details>

<details>
<summary>GDPval-AA v2 — highest first</summary>

| Configuration | GDPval-AA v2 | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 0.631820 | 7.63 |
| Claude Fable 5.1 (xhigh with fallback) | 0.622645 | 5.98 |
| Claude Opus 5 (max) | 0.617545 | 5.86 |
| Claude Opus 5 (xhigh) | 0.604070 | 4.88 |
| Claude Fable 5.1 (high with fallback) | 0.574885 | 3.91 |
| Claude Fable 5 (with fallback) | 0.565730 | 8.75 |
| Claude Opus 5 (high) | 0.564470 | 3.61 |
| GPT-5.6 Sol (max) | 0.562055 | 1.99 |
| GPT-5.6 Sol (xhigh) | 0.542440 | 1.18 |
| GPT-6 Astra (max) | 0.540100 | 3.26 |
| Claude Fable 5.1 (medium with fallback) | 0.539655 | 2.98 |
| GPT-6 Astra (xhigh) | 0.527615 | 2.31 |
| GPT-6 Astra (Non-reasoning) | 0.521295 | 1.71 |
| GPT-6 Astra (high) | 0.514850 | 1.72 |
| Claude Opus 5 (medium) | 0.512435 | 2.19 |
| GPT-5.6 Sol (high) | 0.512005 | 0.81 |
| Claude Fable 5.1 (low with fallback) | 0.501860 | 2.37 |
| Claude Sonnet 5 (max) | 0.500430 | 5.09 |
| GPT-6 Astra (medium) | 0.500335 | 1.54 |
| GPT-5.6 Luna (max) | 0.494665 | 0.18 |
| Claude Opus 4.8 (max) | 0.494520 | 4.08 |
| GPT-5.6 Terra (xhigh) | 0.489300 | 0.63 |
| GPT-5.6 Terra (max) | 0.488480 | 1.40 |
| GPT-5.6 Sol (medium) | 0.478050 | 0.50 |
| GPT-5.6 Luna (xhigh) | 0.464235 | 0.09 |
| GPT-6 Astra (low) | 0.459645 | 0.82 |
| GPT-5.6 Terra (high) | 0.457680 | 0.34 |
| GPT-5.6 Luna (high) | 0.438140 | — |
| Claude Opus 5 (low) | 0.435760 | 1.10 |
| GPT-5.6 Sol (low) | 0.427425 | 0.26 |
| GPT-5.6 Terra (medium) | 0.409685 | — |
| Claude Sonnet 5 (Non-reasoning) | 0.391735 | — |
| Claude Sonnet 5 (medium) | 0.361260 | 1.00 |
| GPT-5.6 Luna (medium) | 0.348210 | — |
| GPT-5.6 Terra (low) | 0.339610 | — |
| GPT-5.6 Terra (Non-reasoning) | 0.334315 | — |
| Claude Sonnet 5 (low) | 0.322520 | 0.51 |
| GPT-5.6 Luna (low) | 0.290895 | — |

</details>

<details>
<summary>AutomationBench-AA — highest first</summary>

| Configuration | AutomationBench-AA | $/task |
| --- | --- | --- |
| GPT-6 Astra (max) | 0.684917 | 3.26 |
| GPT-6 Astra (xhigh) | 0.671778 | 2.31 |
| GPT-6 Astra (high) | 0.666122 | 1.72 |
| GPT-6 Astra (medium) | 0.645950 | 1.54 |
| GPT-6 Astra (Non-reasoning) | 0.617722 | 1.71 |
| GPT-5.6 Sol (max) | 0.600811 | 1.99 |
| GPT-5.6 Terra (max) | 0.596500 | 1.40 |
| Claude Fable 5.1 (max with fallback) | 0.593759 | 7.63 |
| GPT-6 Astra (low) | 0.590967 | 0.82 |
| Claude Fable 5.1 (xhigh with fallback) | 0.577724 | 5.98 |
| Claude Opus 5 (max) | 0.565736 | 5.86 |
| Claude Fable 5.1 (high with fallback) | 0.553231 | 3.91 |
| GPT-5.6 Sol (high) | 0.553122 | 0.81 |
| GPT-5.6 Sol (xhigh) | 0.553117 | 1.18 |
| Claude Fable 5.1 (medium with fallback) | 0.546610 | 2.98 |
| Claude Opus 5 (medium) | 0.543393 | 2.19 |
| Claude Fable 5 (with fallback) | 0.540713 | 8.75 |
| Claude Opus 5 (high) | 0.535640 | 3.61 |
| Claude Opus 5 (xhigh) | 0.532192 | 4.88 |
| Claude Fable 5.1 (low with fallback) | 0.522404 | 2.37 |
| Claude Opus 5 (low) | 0.517907 | 1.10 |
| GPT-5.6 Sol (medium) | 0.513275 | 0.50 |
| GPT-5.6 Luna (max) | 0.502086 | 0.18 |
| GPT-5.6 Terra (xhigh) | 0.471363 | 0.63 |
| Claude Opus 4.8 (max) | 0.455934 | 4.08 |
| GPT-5.6 Luna (xhigh) | 0.425978 | 0.09 |
| GPT-5.6 Terra (high) | 0.420204 | 0.34 |
| GPT-5.6 Sol (low) | 0.409857 | 0.26 |
| Claude Sonnet 5 (max) | 0.365127 | 5.09 |
| GPT-5.6 Luna (high) | 0.355879 | — |
| GPT-5.6 Terra (medium) | 0.335360 | — |
| GPT-5.6 Terra (low) | 0.291064 | — |
| Claude Sonnet 5 (medium) | 0.278722 | 1.00 |
| GPT-5.6 Luna (medium) | 0.230745 | — |
| Claude Sonnet 5 (low) | 0.199019 | 0.51 |
| GPT-5.6 Luna (low) | 0.116922 | — |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| GPT-5.6 Terra (Non-reasoning) | — | — |

</details>

<details>
<summary>Humanity's Last Exam — highest first</summary>

| Configuration | Humanity's Last Exam | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 0.591288 | 7.63 |
| Claude Fable 5.1 (xhigh with fallback) | 0.587118 | 5.98 |
| Claude Fable 5.1 (high with fallback) | 0.559314 | 3.91 |
| Claude Fable 5 (with fallback) | 0.554680 | 8.75 |
| Claude Opus 5 (max) | 0.548656 | 5.86 |
| GPT-6 Astra (max) | 0.546803 | 3.26 |
| GPT-6 Astra (xhigh) | 0.545876 | 2.31 |
| Claude Opus 5 (xhigh) | 0.544022 | 4.88 |
| Claude Fable 5.1 (medium with fallback) | 0.537998 | 2.98 |
| GPT-6 Astra (high) | 0.530584 | 1.72 |
| Claude Opus 5 (high) | 0.528267 | 3.61 |
| GPT-6 Astra (medium) | 0.527340 | 1.54 |
| Claude Opus 5 (medium) | 0.512975 | 2.19 |
| GPT-5.6 Sol (max) | 0.494903 | 1.99 |
| GPT-6 Astra (low) | 0.492122 | 0.82 |
| Claude Fable 5.1 (low with fallback) | 0.488879 | 2.37 |
| Claude Opus 4.8 (max) | 0.486562 | 4.08 |
| GPT-5.6 Sol (xhigh) | 0.473123 | 1.18 |
| GPT-5.6 Sol (high) | 0.460148 | 0.81 |
| Claude Opus 5 (low) | 0.434198 | 1.10 |
| GPT-5.6 Terra (max) | 0.429101 | 1.40 |
| GPT-5.6 Sol (medium) | 0.422150 | 0.50 |
| GPT-5.6 Terra (xhigh) | 0.418906 | 0.63 |
| Claude Sonnet 5 (max) | 0.412882 | 5.09 |
| GPT-5.6 Luna (max) | 0.394810 | 0.18 |
| GPT-5.6 Sol (low) | 0.393883 | 0.26 |
| GPT-5.6 Terra (high) | 0.385079 | 0.34 |
| GPT-6 Astra (Non-reasoning) | 0.371177 | 1.71 |
| GPT-5.6 Luna (xhigh) | 0.369787 | 0.09 |
| GPT-5.6 Luna (high) | 0.334106 | — |
| GPT-5.6 Terra (medium) | 0.332715 | — |
| Claude Sonnet 5 (medium) | 0.299815 | 1.00 |
| GPT-5.6 Terra (low) | 0.291937 | — |
| GPT-5.6 Luna (medium) | 0.257646 | — |
| Claude Sonnet 5 (low) | 0.219184 | 0.51 |
| GPT-5.6 Luna (low) | 0.198332 | — |
| Claude Sonnet 5 (Non-reasoning) | 0.190454 | — |
| GPT-5.6 Terra (Non-reasoning) | 0.113994 | — |

</details>

<details>
<summary>GDP.pdf — highest first</summary>

| Configuration | GDP.pdf | $/task |
| --- | --- | --- |
| GPT-6 Astra (xhigh) | 0.322000 | 2.31 |
| GPT-6 Astra (high) | 0.310000 | 1.72 |
| GPT-6 Astra (max) | 0.310000 | 3.26 |
| GPT-6 Astra (low) | 0.304000 | 0.82 |
| GPT-6 Astra (medium) | 0.304000 | 1.54 |
| Claude Fable 5.1 (low with fallback) | 0.280000 | 2.37 |
| GPT-5.6 Sol (high) | 0.278000 | 0.81 |
| GPT-5.6 Sol (xhigh) | 0.276000 | 1.18 |
| GPT-5.6 Sol (max) | 0.272000 | 1.99 |
| Claude Fable 5.1 (high with fallback) | 0.268000 | 3.91 |
| Claude Fable 5.1 (medium with fallback) | 0.268000 | 2.98 |
| GPT-6 Astra (Non-reasoning) | 0.268000 | 1.71 |
| Claude Fable 5.1 (max with fallback) | 0.262000 | 7.63 |
| Claude Fable 5.1 (xhigh with fallback) | 0.262000 | 5.98 |
| GPT-5.6 Sol (medium) | 0.262000 | 0.50 |
| GPT-5.6 Terra (xhigh) | 0.246000 | 0.63 |
| Claude Fable 5 (with fallback) | 0.240000 | 8.75 |
| GPT-5.6 Luna (max) | 0.240000 | 0.18 |
| GPT-5.6 Terra (max) | 0.240000 | 1.40 |
| GPT-5.6 Luna (xhigh) | 0.238000 | 0.09 |
| Claude Opus 4.8 (max) | 0.228000 | 4.08 |
| Claude Opus 5 (max) | 0.216000 | 5.86 |
| Claude Opus 5 (xhigh) | 0.210000 | 4.88 |
| GPT-5.6 Sol (low) | 0.210000 | 0.26 |
| GPT-5.6 Terra (high) | 0.208000 | 0.34 |
| Claude Opus 5 (medium) | 0.200000 | 2.19 |
| Claude Opus 5 (high) | 0.196000 | 3.61 |
| Claude Opus 5 (low) | 0.172000 | 1.10 |
| Claude Sonnet 5 (max) | 0.132000 | 5.09 |
| Claude Sonnet 5 (medium) | 0.116000 | 1.00 |
| Claude Sonnet 5 (low) | 0.094000 | 0.51 |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| GPT-5.6 Luna (high) | — | — |
| GPT-5.6 Luna (low) | — | — |
| GPT-5.6 Luna (medium) | — | — |
| GPT-5.6 Terra (Non-reasoning) | — | — |
| GPT-5.6 Terra (low) | — | — |
| GPT-5.6 Terra (medium) | — | — |

</details>

<details>
<summary>CritPt — highest first</summary>

| Configuration | CritPt | $/task |
| --- | --- | --- |
| GPT-5.6 Sol (max) | 0.322857 | 1.99 |
| GPT-6 Astra (max) | 0.317143 | 3.26 |
| GPT-6 Astra (xhigh) | 0.314286 | 2.31 |
| Claude Fable 5.1 (xhigh with fallback) | 0.311429 | 5.98 |
| Claude Fable 5.1 (high with fallback) | 0.302857 | 3.91 |
| GPT-5.6 Terra (max) | 0.300000 | 1.40 |
| Claude Fable 5.1 (max with fallback) | 0.297143 | 7.63 |
| Claude Fable 5.1 (medium with fallback) | 0.291429 | 2.98 |
| Claude Opus 5 (max) | 0.291429 | 5.86 |
| GPT-6 Astra (medium) | 0.291429 | 1.54 |
| GPT-6 Astra (high) | 0.288571 | 1.72 |
| GPT-5.6 Sol (xhigh) | 0.285714 | 1.18 |
| Claude Fable 5 (with fallback) | 0.285714 | 8.75 |
| Claude Opus 5 (high) | 0.282857 | 3.61 |
| Claude Fable 5.1 (low with fallback) | 0.277143 | 2.37 |
| Claude Opus 5 (xhigh) | 0.277143 | 4.88 |
| GPT-5.6 Terra (xhigh) | 0.271429 | 0.63 |
| Claude Opus 5 (medium) | 0.268571 | 2.19 |
| GPT-6 Astra (low) | 0.262857 | 0.82 |
| GPT-5.6 Sol (high) | 0.257143 | 0.81 |
| Claude Opus 5 (low) | 0.231429 | 1.10 |
| GPT-5.6 Sol (medium) | 0.228571 | 0.50 |
| GPT-5.6 Terra (high) | 0.228571 | 0.34 |
| Claude Opus 4.8 (max) | 0.208571 | 4.08 |
| GPT-5.6 Luna (max) | 0.205714 | 0.18 |
| GPT-5.6 Luna (xhigh) | 0.205714 | 0.09 |
| GPT-6 Astra (Non-reasoning) | 0.197143 | 1.71 |
| GPT-5.6 Terra (medium) | 0.174286 | — |
| Claude Sonnet 5 (max) | 0.168571 | 5.09 |
| GPT-5.6 Luna (high) | 0.165714 | — |
| GPT-5.6 Sol (low) | 0.148571 | 0.26 |
| GPT-5.6 Terra (low) | 0.094286 | — |
| Claude Sonnet 5 (medium) | 0.085714 | 1.00 |
| GPT-5.6 Luna (medium) | 0.048571 | — |
| Claude Sonnet 5 (low) | 0.045714 | 0.51 |
| GPT-5.6 Luna (low) | 0.025714 | — |
| GPT-5.6 Terra (Non-reasoning) | 0.020000 | — |
| Claude Sonnet 5 (Non-reasoning) | 0.011429 | — |

</details>

<details>
<summary>AA-Omniscience Non-Hallucination Rate — highest first</summary>

This rate is conditional on non-correct responses. Do not read its descending order as a ranking of wrong answers per question; use the derived ranking above.

| Configuration | AA-Omniscience Non-Hallucination Rate | $/task |
| --- | --- | --- |
| Claude Opus 4.8 (max) | 0.607492 | 4.08 |
| Claude Sonnet 5 (max) | 0.606339 | 5.09 |
| GPT-6 Astra (high) | 0.552316 | 1.72 |
| GPT-6 Astra (medium) | 0.534658 | 1.54 |
| GPT-6 Astra (low) | 0.530890 | 0.82 |
| GPT-6 Astra (xhigh) | 0.516820 | 2.31 |
| GPT-6 Astra (max) | 0.486631 | 3.26 |
| Claude Sonnet 5 (Non-reasoning) | 0.479607 | — |
| Claude Opus 5 (xhigh) | 0.404527 | 4.88 |
| Claude Opus 5 (medium) | 0.393245 | 2.19 |
| Claude Opus 5 (max) | 0.391823 | 5.86 |
| Claude Opus 5 (high) | 0.387921 | 3.61 |
| Claude Opus 5 (low) | 0.377980 | 1.10 |
| Claude Fable 5 (with fallback) | 0.363636 | 8.75 |
| GPT-6 Astra (Non-reasoning) | 0.345721 | 1.71 |
| Claude Fable 5.1 (low with fallback) | 0.343671 | 2.37 |
| Claude Fable 5.1 (high with fallback) | 0.311787 | 3.91 |
| Claude Fable 5.1 (medium with fallback) | 0.308943 | 2.98 |
| Claude Sonnet 5 (medium) | 0.301007 | 1.00 |
| Claude Fable 5.1 (xhigh with fallback) | 0.294524 | 5.98 |
| Claude Fable 5.1 (max with fallback) | 0.274161 | 7.63 |
| Claude Sonnet 5 (low) | 0.272413 | 0.51 |
| GPT-5.6 Terra (max) | 0.121241 | 1.40 |
| GPT-5.6 Terra (xhigh) | 0.109820 | 0.63 |
| GPT-5.6 Sol (low) | 0.105837 | 0.26 |
| GPT-5.6 Terra (medium) | 0.102286 | — |
| GPT-5.6 Terra (high) | 0.102109 | 0.34 |
| GPT-5.6 Terra (low) | 0.101303 | — |
| GPT-5.6 Luna (low) | 0.101297 | — |
| GPT-5.6 Sol (medium) | 0.092308 | 0.50 |
| GPT-5.6 Luna (medium) | 0.091343 | — |
| GPT-5.6 Sol (high) | 0.088035 | 0.81 |
| GPT-5.6 Sol (xhigh) | 0.081344 | 1.18 |
| GPT-5.6 Sol (max) | 0.077997 | 1.99 |
| GPT-5.6 Luna (high) | 0.076152 | — |
| GPT-5.6 Luna (xhigh) | 0.075297 | 0.09 |
| GPT-5.6 Luna (max) | 0.074214 | 0.18 |
| GPT-5.6 Terra (Non-reasoning) | 0.049855 | — |

</details>

<details>
<summary>Harvey LAB-AA — highest first</summary>

| Configuration | Harvey LAB-AA | $/task |
| --- | --- | --- |
| Claude Fable 5 (with fallback) | 0.935591 | 8.75 |
| Claude Opus 5 (max) | 0.934578 | 5.86 |
| Claude Fable 5.1 (xhigh with fallback) | 0.932696 | 5.98 |
| Claude Fable 5.1 (max with fallback) | 0.930236 | 7.63 |
| Claude Fable 5.1 (high with fallback) | 0.929512 | 3.91 |
| Claude Fable 5.1 (medium with fallback) | 0.926473 | 2.98 |
| Claude Fable 5.1 (low with fallback) | 0.923288 | 2.37 |
| Claude Opus 4.8 (max) | 0.910841 | 4.08 |
| Claude Sonnet 5 (max) | 0.900709 | 5.09 |
| GPT-5.6 Luna (max) | 0.878998 | 0.18 |
| GPT-5.6 Sol (max) | 0.871761 | 1.99 |
| GPT-5.6 Terra (max) | 0.851788 | 1.40 |
| Claude Opus 5 (high) | — | 3.61 |
| Claude Opus 5 (low) | — | 1.10 |
| Claude Opus 5 (medium) | — | 2.19 |
| Claude Opus 5 (xhigh) | — | 4.88 |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| Claude Sonnet 5 (low) | — | 0.51 |
| Claude Sonnet 5 (medium) | — | 1.00 |
| GPT-5.6 Luna (high) | — | — |
| GPT-5.6 Luna (low) | — | — |
| GPT-5.6 Luna (medium) | — | — |
| GPT-5.6 Luna (xhigh) | — | 0.09 |
| GPT-5.6 Sol (high) | — | 0.81 |
| GPT-5.6 Sol (low) | — | 0.26 |
| GPT-5.6 Sol (medium) | — | 0.50 |
| GPT-5.6 Sol (xhigh) | — | 1.18 |
| GPT-5.6 Terra (Non-reasoning) | — | — |
| GPT-5.6 Terra (high) | — | 0.34 |
| GPT-5.6 Terra (low) | — | — |
| GPT-5.6 Terra (medium) | — | — |
| GPT-5.6 Terra (xhigh) | — | 0.63 |
| GPT-6 Astra (Non-reasoning) | — | 1.71 |
| GPT-6 Astra (high) | — | 1.72 |
| GPT-6 Astra (low) | — | 0.82 |
| GPT-6 Astra (max) | — | 3.26 |
| GPT-6 Astra (medium) | — | 1.54 |
| GPT-6 Astra (xhigh) | — | 2.31 |

</details>

<details>
<summary>EnterpriseOps-Gym-AA — highest first</summary>

| Configuration | EnterpriseOps-Gym-AA | $/task |
| --- | --- | --- |
| Claude Fable 5 (with fallback) | 0.511191 | 8.75 |
| Claude Opus 5 (max) | 0.474784 | 5.86 |
| Claude Sonnet 5 (max) | 0.446732 | 5.09 |
| Claude Opus 4.8 (max) | 0.439570 | 4.08 |
| GPT-5.6 Sol (max) | 0.429126 | 1.99 |
| GPT-5.6 Luna (max) | 0.408236 | 0.18 |
| GPT-5.6 Terra (max) | 0.384960 | 1.40 |
| Claude Fable 5.1 (high with fallback) | — | 3.91 |
| Claude Fable 5.1 (low with fallback) | — | 2.37 |
| Claude Fable 5.1 (max with fallback) | — | 7.63 |
| Claude Fable 5.1 (medium with fallback) | — | 2.98 |
| Claude Fable 5.1 (xhigh with fallback) | — | 5.98 |
| Claude Opus 5 (high) | — | 3.61 |
| Claude Opus 5 (low) | — | 1.10 |
| Claude Opus 5 (medium) | — | 2.19 |
| Claude Opus 5 (xhigh) | — | 4.88 |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| Claude Sonnet 5 (low) | — | 0.51 |
| Claude Sonnet 5 (medium) | — | 1.00 |
| GPT-5.6 Luna (high) | — | — |
| GPT-5.6 Luna (low) | — | — |
| GPT-5.6 Luna (medium) | — | — |
| GPT-5.6 Luna (xhigh) | — | 0.09 |
| GPT-5.6 Sol (high) | — | 0.81 |
| GPT-5.6 Sol (low) | — | 0.26 |
| GPT-5.6 Sol (medium) | — | 0.50 |
| GPT-5.6 Sol (xhigh) | — | 1.18 |
| GPT-5.6 Terra (Non-reasoning) | — | — |
| GPT-5.6 Terra (high) | — | 0.34 |
| GPT-5.6 Terra (low) | — | — |
| GPT-5.6 Terra (medium) | — | — |
| GPT-5.6 Terra (xhigh) | — | 0.63 |
| GPT-6 Astra (Non-reasoning) | — | 1.71 |
| GPT-6 Astra (high) | — | 1.72 |
| GPT-6 Astra (low) | — | 0.82 |
| GPT-6 Astra (max) | — | 3.26 |
| GPT-6 Astra (medium) | — | 1.54 |
| GPT-6 Astra (xhigh) | — | 2.31 |

</details>

<details>
<summary>AA-AnalystAgent — highest first</summary>

| Configuration | AA-AnalystAgent | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 0.575000 | 7.63 |
| Claude Opus 5 (max) | 0.537500 | 5.86 |
| GPT-6 Astra (max) | 0.512500 | 3.26 |
| Claude Fable 5 (with fallback) | 0.487500 | 8.75 |
| GPT-5.6 Sol (max) | 0.475000 | 1.99 |
| Claude Sonnet 5 (max) | 0.462500 | 5.09 |
| Claude Opus 4.8 (max) | 0.450000 | 4.08 |
| Claude Fable 5.1 (high with fallback) | — | 3.91 |
| Claude Fable 5.1 (low with fallback) | — | 2.37 |
| Claude Fable 5.1 (medium with fallback) | — | 2.98 |
| Claude Fable 5.1 (xhigh with fallback) | — | 5.98 |
| Claude Opus 5 (high) | — | 3.61 |
| Claude Opus 5 (low) | — | 1.10 |
| Claude Opus 5 (medium) | — | 2.19 |
| Claude Opus 5 (xhigh) | — | 4.88 |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| Claude Sonnet 5 (low) | — | 0.51 |
| Claude Sonnet 5 (medium) | — | 1.00 |
| GPT-5.6 Luna (high) | — | — |
| GPT-5.6 Luna (low) | — | — |
| GPT-5.6 Luna (max) | — | 0.18 |
| GPT-5.6 Luna (medium) | — | — |
| GPT-5.6 Luna (xhigh) | — | 0.09 |
| GPT-5.6 Sol (high) | — | 0.81 |
| GPT-5.6 Sol (low) | — | 0.26 |
| GPT-5.6 Sol (medium) | — | 0.50 |
| GPT-5.6 Sol (xhigh) | — | 1.18 |
| GPT-5.6 Terra (Non-reasoning) | — | — |
| GPT-5.6 Terra (high) | — | 0.34 |
| GPT-5.6 Terra (low) | — | — |
| GPT-5.6 Terra (max) | — | 1.40 |
| GPT-5.6 Terra (medium) | — | — |
| GPT-5.6 Terra (xhigh) | — | 0.63 |
| GPT-6 Astra (Non-reasoning) | — | 1.71 |
| GPT-6 Astra (high) | — | 1.72 |
| GPT-6 Astra (low) | — | 0.82 |
| GPT-6 Astra (medium) | — | 1.54 |
| GPT-6 Astra (xhigh) | — | 2.31 |

</details>

<details>
<summary>IFBench — highest first</summary>

| Configuration | IFBench | $/task |
| --- | --- | --- |
| GPT-5.6 Sol (max) | 0.726531 | 1.99 |
| GPT-5.6 Terra (max) | 0.712245 | 1.40 |
| GPT-5.6 Sol (xhigh) | 0.710204 | 1.18 |
| GPT-5.6 Sol (medium) | 0.695918 | 0.50 |
| GPT-5.6 Sol (high) | 0.691837 | 0.81 |
| GPT-5.6 Sol (low) | 0.665306 | 0.26 |
| GPT-5.6 Terra (xhigh) | 0.662585 | 0.63 |
| GPT-5.6 Terra (high) | 0.644218 | 0.34 |
| Claude Fable 5 (with fallback) | 0.634694 | 8.75 |
| Claude Opus 4.8 (max) | 0.622449 | 4.08 |
| GPT-5.6 Terra (medium) | 0.621769 | — |
| GPT-5.6 Terra (low) | 0.596599 | — |
| Claude Fable 5.1 (high with fallback) | — | 3.91 |
| Claude Fable 5.1 (low with fallback) | — | 2.37 |
| Claude Fable 5.1 (max with fallback) | — | 7.63 |
| Claude Fable 5.1 (medium with fallback) | — | 2.98 |
| Claude Fable 5.1 (xhigh with fallback) | — | 5.98 |
| Claude Opus 5 (high) | — | 3.61 |
| Claude Opus 5 (low) | — | 1.10 |
| Claude Opus 5 (max) | — | 5.86 |
| Claude Opus 5 (medium) | — | 2.19 |
| Claude Opus 5 (xhigh) | — | 4.88 |
| Claude Sonnet 5 (Non-reasoning) | — | — |
| Claude Sonnet 5 (low) | — | 0.51 |
| Claude Sonnet 5 (max) | — | 5.09 |
| Claude Sonnet 5 (medium) | — | 1.00 |
| GPT-5.6 Luna (high) | — | — |
| GPT-5.6 Luna (low) | — | — |
| GPT-5.6 Luna (max) | — | 0.18 |
| GPT-5.6 Luna (medium) | — | — |
| GPT-5.6 Luna (xhigh) | — | 0.09 |
| GPT-5.6 Terra (Non-reasoning) | — | — |
| GPT-6 Astra (Non-reasoning) | — | 1.71 |
| GPT-6 Astra (high) | — | 1.72 |
| GPT-6 Astra (low) | — | 0.82 |
| GPT-6 Astra (max) | — | 3.26 |
| GPT-6 Astra (medium) | — | 1.54 |
| GPT-6 Astra (xhigh) | — | 2.31 |

</details>

<details>
<summary>𝜏³-Banking — highest first</summary>

| Configuration | 𝜏³-Banking | $/task |
| --- | --- | --- |
| Claude Fable 5.1 (max with fallback) | 0.472165 | 7.63 |
| Claude Fable 5.1 (xhigh with fallback) | 0.457732 | 5.98 |
| Claude Opus 5 (high) | 0.447423 | 3.61 |
| GPT-5.6 Sol (max) | 0.443299 | 1.99 |
| Claude Opus 5 (xhigh) | 0.432990 | 4.88 |
| Claude Fable 5.1 (high with fallback) | 0.430928 | 3.91 |
| GPT-6 Astra (xhigh) | 0.430928 | 2.31 |
| Claude Opus 5 (max) | 0.420619 | 5.86 |
| GPT-6 Astra (max) | 0.414433 | 3.26 |
| Claude Fable 5.1 (medium with fallback) | 0.410309 | 2.98 |
| GPT-5.6 Terra (max) | 0.402062 | 1.40 |
| GPT-6 Astra (high) | 0.400000 | 1.72 |
| Claude Fable 5.1 (low with fallback) | 0.389691 | 2.37 |
| Claude Opus 5 (medium) | 0.385567 | 2.19 |
| Claude Fable 5 (with fallback) | 0.381443 | 8.75 |
| GPT-5.6 Sol (xhigh) | 0.381443 | 1.18 |
| Claude Sonnet 5 (max) | 0.373196 | 5.09 |
| GPT-6 Astra (Non-reasoning) | 0.371134 | 1.71 |
| GPT-5.6 Sol (high) | 0.367010 | 0.81 |
| GPT-5.6 Sol (medium) | 0.364948 | 0.50 |
| GPT-6 Astra (medium) | 0.354639 | 1.54 |
| Claude Opus 4.8 (max) | 0.342268 | 4.08 |
| GPT-6 Astra (low) | 0.319588 | 0.82 |
| GPT-5.6 Luna (max) | 0.311340 | 0.18 |
| Claude Opus 5 (low) | 0.303093 | 1.10 |
| GPT-5.6 Terra (xhigh) | 0.296907 | 0.63 |
| GPT-5.6 Sol (low) | 0.290722 | 0.26 |
| GPT-5.6 Luna (xhigh) | 0.286598 | 0.09 |
| GPT-5.6 Terra (high) | 0.286598 | 0.34 |
| GPT-5.6 Terra (medium) | 0.255670 | — |
| GPT-5.6 Luna (high) | 0.251546 | — |
| GPT-5.6 Terra (low) | 0.187629 | — |
| GPT-5.6 Luna (medium) | 0.177320 | — |
| Claude Sonnet 5 (Non-reasoning) | 0.156701 | — |
| GPT-5.6 Terra (Non-reasoning) | 0.156701 | — |
| GPT-5.6 Luna (low) | 0.127835 | — |
| Claude Sonnet 5 (low) | — | 0.51 |
| Claude Sonnet 5 (medium) | — | 1.00 |

</details>

<details>
<summary>MMMU-Pro — highest first</summary>

| Configuration | MMMU-Pro | $/task |
| --- | --- | --- |
| GPT-6 Astra (max) | 0.868786 | 3.26 |
| GPT-6 Astra (high) | 0.864162 | 1.72 |
| GPT-6 Astra (xhigh) | 0.862428 | 2.31 |
| GPT-6 Astra (medium) | 0.850867 | 1.54 |
| Claude Opus 5 (max) | 0.847399 | 5.86 |
| GPT-6 Astra (low) | 0.846243 | 0.82 |
| Claude Opus 5 (xhigh) | 0.839884 | 4.88 |
| GPT-5.6 Sol (max) | 0.834104 | 1.99 |
| GPT-5.6 Sol (xhigh) | 0.826590 | 1.18 |
| Claude Opus 5 (high) | 0.824277 | 3.61 |
| GPT-6 Astra (Non-reasoning) | 0.820231 | 1.71 |
| GPT-5.6 Sol (high) | 0.818497 | 0.81 |
| Claude Opus 5 (medium) | 0.816185 | 2.19 |
| GPT-5.6 Sol (medium) | 0.813873 | 0.50 |
| GPT-5.6 Sol (low) | 0.809827 | 0.26 |
| GPT-5.6 Terra (max) | 0.806936 | 1.40 |
| Claude Opus 5 (low) | 0.798266 | 1.10 |
| GPT-5.6 Terra (xhigh) | 0.794798 | 0.63 |
| GPT-5.6 Terra (high) | 0.790751 | 0.34 |
| GPT-5.6 Luna (max) | 0.785549 | 0.18 |
| GPT-5.6 Luna (xhigh) | 0.785549 | 0.09 |
| GPT-5.6 Luna (high) | 0.775723 | — |
| Claude Sonnet 5 (max) | 0.772832 | 5.09 |
| GPT-5.6 Terra (medium) | 0.767630 | — |
| GPT-5.6 Terra (low) | 0.761272 | — |
| GPT-5.6 Luna (medium) | 0.758382 | — |
| GPT-5.6 Luna (low) | 0.739884 | — |
| Claude Sonnet 5 (Non-reasoning) | 0.719075 | — |
| GPT-5.6 Terra (Non-reasoning) | 0.667052 | — |
| Claude Fable 5 (with fallback) | — | 8.75 |
| Claude Fable 5.1 (high with fallback) | — | 3.91 |
| Claude Fable 5.1 (low with fallback) | — | 2.37 |
| Claude Fable 5.1 (max with fallback) | — | 7.63 |
| Claude Fable 5.1 (medium with fallback) | — | 2.98 |
| Claude Fable 5.1 (xhigh with fallback) | — | 5.98 |
| Claude Opus 4.8 (max) | — | 4.08 |
| Claude Sonnet 5 (low) | — | 0.51 |
| Claude Sonnet 5 (medium) | — | 1.00 |

</details>

## Selection implications

The [interpretation notes](model-selection-analysis.md) explain how these results inform suggested starting points. The [operational model guide](../references/model-selection.md) contains choices and constraints without loading these tables. Rebuild with `python docs/benchmarks/tools/combine-model-evidence.py`; use `--check` to verify reproducibility. This process reads the workbooks without altering them.
