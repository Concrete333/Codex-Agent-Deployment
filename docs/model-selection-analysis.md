# Model-selection analysis

Reviewed 9 September 2026. Maintenance evidence, not operational skill context.

## Source material

The [combined comparison](model-performance-comparison.md) reconciles 22 GPT and 16 Claude configurations from the 8 September capture. It retains configuration labels, missing values and GPT score-status flags. Costs, tokens and all 17 evaluation columns are available there; model choices should not rest on the composite alone.

The [Claude-only workbook](benchmarks/claude-model-evidence-2026-09-08.xlsx) was copied unchanged from `Claude-Agent-Deployment/docs/benchmarks/claude-model-evidence-2026-09-08.xlsx`, at source repository commit `231fc6b582284d5627f4fd737a76ae8c35a49366`. Its SHA-256 is `a023802ec47170f0e1216e5fcf3f759395faddadc1dcad1eae0285ac95006645`. It contains 16 Claude configurations and no GPT model rows.

GPT data comes from the [raw capture](benchmarks/openai-metrics-raw-2026-09-08.json), checked against the [corrected GPT workbook](benchmarks/GPT-model-efficiency-2026-09-08.xlsx). The combined document is generated reproducibly by [combine-model-evidence.py](benchmarks/tools/combine-model-evidence.py). No source workbook is modified.

## Selection objective

Choose the lowest total-cost workflow that meets a defined correctness requirement. Speed is not a routing objective. Include coordinator context, verification, handoffs, corrections and integration. A benchmark score or cost-per-point ratio cannot establish cost per accepted repository task.

The captured dollar figure is a **suite-wide average**, not the cost of running each individual evaluation. Comparing a task-specific score with that average is useful screening evidence, not an exact task-specific cost frontier. Scores below remain candidate-selection evidence; no controlled deployment test has established equal accuracy on our assignments.

## General shortlist

| Candidate | Captured evidence | Interpretation |
| --- | --- | --- |
| Luna Max | $0.18/task; AA-LCR 83.7%; Terminal-Bench 11.6%; wrong answers/question 53.0%. | Bounded, source-grounded extraction and mechanically checkable edits. Not an autonomous design or factual authority. |
| Astra Light | $0.82; Terminal-Bench 41.9%; wrong/question 19.0%. Sol High costs $0.81 with Terminal-Bench 20.7%. | Initial candidate for specified implementation and bounded diagnosis with dependable checks. No measured basis for requiring a Sol diagnostic pass first. |
| Astra Medium | $1.54; Terminal-Bench 49.5%. | Retain when it already meets the acceptance requirement. Do not require it as an intermediate step. |
| Astra High | $1.72; Terminal-Bench 54.0%; wrong/question 17.4%. | Candidate for difficult diagnosis, coupled implementation and subtle correctness review. Its 11.7% cost premium over Medium accompanies a 4.5-point Terminal-Bench increase, not a proven improvement on every task. |
| Astra X-High | $2.31; Terminal-Bench 59.6%. | Candidate for harder repository reasoning. Compared with High, 34.3% more cost accompanies a 5.6-point increase. |
| Astra Max | $3.26; Terminal-Bench 59.1%. | No routine general-coding role: 41.1% more cost than X-High without an observed gain on this metric. Other task-specific gains can justify an exception. |

Luna X-High costs $0.09 with AA-LCR 81.7%, versus Max's $0.18 and 83.7%. It is a candidate for a controlled comparison on the simplest objectively checked work, not a demonstrated accuracy-preserving substitution. Max remains the operational Luna configuration.

## Specialist choices

| Task shape | Evidence | Selection implication |
| --- | --- | --- |
| Scientific Python subproblems | Sol Low/Medium/High/Max: SciCode 56.4%/57.4%/57.8%/57.1% at $0.26/$0.50/$0.81/$1.99. | Low/Medium are economical initial candidates with executable checks. Higher effort is not automatically better. SciCode does not establish autonomous repository competence. |
| Demanding scientific coding | Fable 5.1 High/X-High/Max **with fallback**: SciCode 58.7%/60.9%/63.1% at $3.91/$5.98/$7.63. | Consider the premium when a cheaper candidate does not meet the scientific reasoning requirement. Max needs a specific unmet quality requirement. |
| Difficult general coding | Fable X-High **with fallback**: Terminal-Bench 55.1% at $5.98, versus Astra X-High 59.6% at $2.31. | Do not offer Fable X-High as a routine coding upgrade. Its specialist advantages are a different case. |
| Professional deliverables | Sol has economical intermediate results; Fable High/X-High perform strongly on AA-Briefcase and GDPval-AA. | Candidates for business analysis and deliverable production against an explicit rubric. The stored normalized scores are not success percentages. A higher composite score is not a substitute for checking the deliverable. |
| Research-level physics | Sol Max leads the captured CritPt results at 32.3%, with $1.99 suite-average cost. Some Terra configurations also offer inexpensive competitive results. | Preserve domain-specific exceptions rather than banning families by composite rank. Do not extrapolate to all hard reasoning. |
| Factual reliability | Astra High: 17.4% wrong/question, 61.1% accuracy, $1.72. Opus 4.8 Max: 20.1%, 48.8%, $4.08. Fable X-High: 23.8%, 66.2%, $5.98. | No standing Opus verifier. Astra Light/High are candidates where incorrect answers are costly. Fable's additional knowledge coverage also brings more incorrect answers than Astra High; verify claims. None of these measures tests source-checking skill. |
| Enterprise operations and analyst work | Some higher Opus efforts, Fable 5 and Sol Max have relevant results. Many other model/effort combinations are missing. | Retain as narrow exceptions requiring task-specific evidence. Missing data does not establish inferiority, and sparse coverage does not support a general effort ladder. |

Opus Low/Medium are not default cross-provider implementation alternatives: their Terminal-Bench scores are 26.3%/34.3% at $1.10/$2.19, versus Astra Light/High's 41.9%/54.0% at $0.82/$1.72. Authorized Claude-only access, account preference, retained context or demonstrated task-specific results can still justify them.

The operational model guide combines acceptance examples, a limited cost reference, direct family comparisons and effort guidance. It includes enough evidence-derived context to choose without loading these research tables, but does not give every GPT recommendation a Claude counterpart. The effort-to-task mappings are starting hypotheses, not measured guarantees. Sol's prior debugger/hardening role and an automatic Opus verifier are not supported as general rules by this data.

## Limits that affect deployment

- API-priced benchmark averages are not Codex or Claude subscription allowance consumption. Real accepted-task cost includes parent input, cache writes/hits, retries, checks, integration and helper calls. No cross-subscription savings percentage is established here.
- Claude Fable configurations are explicitly labeled **with fallback**. The wrapper does not set a fallback model. The capture supports candidate selection, not a guarantee that a Fable-only CLI worker reproduces those results.
- Wrong answers per question are derived as `(1 − accuracy) × (1 − non-hallucination rate)`. Comparing the conditional non-hallucination rate directly answers a different question. Neither measure tests source verification or predicts coding defects.
- A frontier based on composite score and price is a narrow mathematical result. Small index differences are uncertain; task-specific outcomes and harness differences matter. Do not turn frontier membership into a whitelist.
- Six GPT configurations have estimated scores and missing cost data. Claude's workbook has no score-status field. Missing measurements must not become zeros or inferred guarantees.
- Prior local live tests established that Opus 5 Low can read this repository through the wrapper. They did not establish a cross-model ranking or validate every Claude model/effort on this account. Offline wrapper tests check argument handling and safeguards, not model quality.

## Coordination implications

The [coordination references](agent-coordination-references.md) favor the simplest adequate workflow, checkable assignments, context isolation when it helps, and coherent ownership of dependent changes. They do not prove a universal model-role mapping or that multiple agents save money.

The operational guide therefore offers candidate configurations while keeping requirements, permissions, evidence and acceptance firm. It avoids mandatory specialist chains, duplicate reasoning committees, automatic review passes and repeated empty polling. Parallel work must have independent decisions and safe write ownership. Failures prompt a diagnosis of the limitation, not a traversal of every model.

## Vendor guidance

- [OpenAI's current-model guide](https://developers.openai.com/api/docs/guides/latest-model) provides Astra capability and effort context; it does not establish our role assignments.
- [Anthropic's Fable 5.1 overview](https://platform.claude.com/docs/en/models/fable-5-1/overview) identifies difficult, long-horizon work as a use case while retaining Opus 5 for other workloads.
- [Fable prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) and [effort documentation](https://platform.claude.com/docs/en/build-with-claude/effort) support testing effort for the task instead of treating equal labels as equivalent across families.

Evaluate changes on bounded tasks with the same requirements, starting state and acceptance checks as a suitable single-agent baseline. Record accepted outcomes, missed defects and complete workflow cost. Change the starting recommendations when that evidence warrants it.
