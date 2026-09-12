# Handoff: audit our delegation work and test the Claude skill

Prepared 10 September 2026. This is maintenance material, not context for ordinary skill use.

For the later two lower-cost adapter trials, use the
[adapter benchmark handoff](claude-adapter-benchmark-handoff-2026-09-10.md).
It includes the frozen repeat and subsequently discovered reference-coverage gap;
the policy and status descriptions below are historical.

## What we want you to do

Audit the Codex Agent Deployment skill, the experiments below and our conclusions. Then adapt the useful mechanisms and experimental design to the Claude Agent Deployment skill. Challenge our interpretation; do not import our model assignments or assume delegation must win.

The objective is **lower total cost to an accepted result without reducing required accuracy**. Speed is not a goal. An inexpensive worker, a passing self-check or a cheaper unfinished attempt is not sufficient evidence of success.

Local repositories:

- Codex: `C:\Users\cwbec\Codex-Agent-Deployment`
- Claude: `C:\Users\cwbec\Claude-Agent-Deployment`
- Installed Codex skill: `C:\Users\cwbec\.codex\skills\agent-deployment`

Read each repository's applicable `AGENTS.md` and `CLAUDE.md` before working there. Relevant research and benchmark documents may be read during maintenance and audits; ordinary deployment should not load them. Keep any resulting operational changes short and actionable, with evidence and caveats in docs.

This report contains evaluation answers. **You are now unblinded.** Do not use this conversation as the context for a benchmark participant. Use fresh isolated sessions supplied only their assigned task, permitted policy and source material.

## Current state, not necessarily GitHub state

At handoff, Codex HEAD is `c095231`. There are pending changes to `.gitignore`, `README.md`, `SKILL.md` and `references/model-selection.md`; the entire `docs/benchmarks/prose-migration/` directory is also uncommitted. Inspect the working tree, not just GitHub. Preserve the original receipts and frozen policy snapshots. The installed core and guide were synchronized after the latest policy edit; verify before relying on that again.

The latest policy edit introduced a single substantive verification owner. Subsequent Sol and Opus diagnostics did **not** validate cheaper review as an accuracy-preserving replacement. We have not revised the skill again in response to those results. That gap deserves review.

No new benchmark or Claude-skill edit is performed by this handoff. Establish the proposed trial scope and spending bounds before starting new paid runs; do not interpret it as unlimited retry authorization.

## How the skill evolved

We began with model-specialist routing based on external performance and cost data. Local tests shifted attention toward coordinator overhead, actual ownership and the cost of verification.

Current Codex policy:

- Keep small or coupled work local. Prefer scripts for deterministic work.
- Before dispatch, name work the coordinator will stop doing and a check that does not require solving it again. Do not write the full solution just to make a cheap worker usable.
- The coordinator owns consequential decisions and acceptance. Give a worker bounded scope, settled interfaces, relevant evidence and explicit checks; leave local implementation choices to it.
- Prefer one owner for coupled implementation, tests and corrections. Independent review must address a named risk or replace meaningful coordinator work.
- Allowed workers are Luna, Terra, Sol and Opus 5. No Astra or Fable workers. Luna uses Max only. Keep the current orchestrator's model and effort.
- Use minimal inherited context, explicit configuration, independent write ownership and completion waits. Do not duplicate an active assignment or replace a worker because a wait timed out.
- Select one substantive verification owner. That owner checks original evidence; the coordinator checks the resulting evidence, gaps and unresolved findings without automatically repeating the full review. Required coverage cannot be replaced by sampling.
- Preserve acceptance criteria. Process completion and self-reported success are not acceptance. One substantive non-trivial Luna failure ends that attempt; routine tool corrections are not such failures.

These are the user's Codex constraints, **not instructions to add GPT workers to the Claude skill**. Inspect the Claude skill's current models, controls and constraints independently.

## Evidence to read

Start with this report, the current [core skill](../SKILL.md), [model guide](../references/model-selection.md), then the relevant result reports below. Load larger references only for the question being audited.

- [Coordination references](agent-coordination-references.md): research and engineering sources, with premise, takeaway and limitations. The main lessons concern context isolation, dependencies, verification and whole-workflow cost. They do not establish a universal worker ladder or a 45% model-score cutoff.
- [Combined model comparison](model-performance-comparison.md): captured GPT and Claude performance/cost evidence, with source workbooks. [Selection analysis](model-selection-analysis.md) records interpretation, including historical recommendations that may differ from current policy.
- [Claude-only workbook](benchmarks/claude-model-evidence-2026-09-08.xlsx) and [GPT workbook](benchmarks/GPT-model-efficiency-2026-09-08.xlsx): reference data, not deployment-time inputs.
- [Claude execution guide](../references/claude-cli.md) and [wrapper](../scripts/claude_worker.py): how Codex invokes a real Claude Code session, with model, effort, permissions, structured receipts and continuation. This is not itself a benchmark of native Claude orchestration.

Important inherited data cautions: suite-average dollars per task are not our task costs or subscription allowance. Composite benchmark points are not units of useful work. Luna Max's corrected Intelligence Index is 37.5; 35.4 was a briefing transcription error. AA's non-hallucination measure is conditional on non-correct responses: using fractions, `wrong/all = (1 - accuracy) * (1 - nonhall)`. Comparing the conditional rate alone produced a backwards effort recommendation in earlier Claude work. Factual recall metrics also do not directly measure source verification.

## What we actually measured

All dollar figures below are captured **API-equivalent estimates**, not subscription charges or measured allowance consumption. Trial totals exclude experiment preparation, supervising this research and external evaluation. Those activities are real overhead, not free production verification. Worker-only diagnostics exclude additional coordinator acceptance and repairs too.

### Earlier coding and routing tests

| Experiment | Solo, no skill | Other condition | Result |
| --- | ---: | ---: | --- |
| cattrs feature | $1.436838 | Unguided delegation: $2.452440 | Both completed; 16 feature checks and 265 regressions passed |
| Same cattrs feature | $1.436838 | Skill + Luna Max: at least $3.021813 | Saved code passed the same checks, but the run timed out before final completion |
| Revised-skill three-task comparison | $1.326736 total | Skill: $1.653674 total | All six runs passed frozen checks; all three skill participants stayed solo |

In cattrs, the skill's Luna worker cost $0.051451, while its Astra High coordinator cost $2.970362. Native waiting worked; no busy-polling loop explained that result. The timeout makes its recorded cost a lower bound and its workflow partial.

The revised-skill tasks were interval repair, catalogue investigation and an idempotency component. Skill overhead was 24.6% in aggregate, but this did not test worker effectiveness: none spawned. The large catalogue could be processed economically with a script. Extra component review also caught a valid huge-integer TTL case missed by the baseline and frozen checker. Do not call all additional checking waste or assume equal correctness from equal frozen scores.

Sources: [cattrs results](benchmarks/cattrs-self/results-2026-09-10.md), [revised-skill results](benchmarks/revision-ab/results-2026-09-10.md). Earlier development runs remain under `benchmarks/pilot/` and `benchmarks/dual-service/`; they used earlier policies. Condition labels are local to each report: the revised-skill two-arm report calls its skill arm B, although its runner retained C.

### Latest task: interpreting a substantial prose corpus

We constructed 50 independent synthetic discussions about a fictional Harbor 4.0 migration: 12,907 words, 95,658 source bytes. Participants classify operator actions as required, conditional, unnecessary or unresolved, and return JSON with concise explanations and exact, line-cited quotations. Chronology, withdrawals, scope and unresolved proposals matter. The 2031 evidence cutoff is fictional task data, not the test date.

The frozen grader checks all IDs, labels, schema, dates, lengths, exact quotes, line bounds and unchanged sources. It **does not grade semantic fidelity of explanations**. We also reviewed those explanations against the sources. This was unblinded model evaluation, not independent human adjudication.

| Condition | Configuration | Cost | Result |
| --- | --- | ---: | --- |
| A: solo | Astra High, no skill, delegation disabled | $1.299660 | 50/50 labels and citations; one semantic scope correction needed |
| C: optional delegation | Astra High + skill; chose solo | $1.325202 | Same automated scores and same semantic issue |
| D: forced worker | Astra High + skill + exactly one Luna Max | $1.6628482 | Same automated scores; no material issue found after internal corrections |

C cost 1.97% more than A. D cost 27.94% more than A, but A was never repaired, so this is **not a comparison of equally accepted final results**. There was no unguided B arm for this corpus. D tests forced delegation, not the skill's spontaneous routing choice.

In D, Luna's entire work cost **$0.1013802**. Astra cost **$1.561468**, or 93.9% of the total. Astra reread all 50 source discussions and the answer, then requested corrections. We displaced answer writing, but not the expensive source-reading and verification work. Luna's correction pass itself cost only $0.0145544.

The trace shows one spawn, one follow-up and two genuine completion waits. No polling loop, premature worker replacement or interruption occurred. Waiting improvements cannot explain away this result.

Sources: [setup and runners](benchmarks/prose-migration/README.md), [A/C results](benchmarks/prose-migration/results-2026-09-10.md), [forced Luna results](benchmarks/prose-migration/results-forced-luna-2026-09-10.md), [semantic review](benchmarks/prose-migration/semantic-review.md).

### Can cheaper review or a stronger writer remove that cost?

We then ran three isolated worker diagnostics. These are **not full skill/no-skill comparisons**.

| Diagnostic | Cost | Outcome |
| --- | ---: | --- |
| Sol High reviews initial Luna answer | $0.5635768 | Found one of three previously identified concerns; missed a substantive meaning reversal |
| Opus 5 Low owns complete answer and self-checks | $1.02065325 | 50/50 labels, only 45/50 valid citation records; not accepted |
| Opus 5 Low reviews the same initial Luna answer | $0.58429925 | Read every source, returned no findings; missed all three comparison concerns |

Both reviewers received the original task, sources and **uncorrected initial Luna answer**, without known defects, a finding count, gold labels or research. Sol had shell-enabled read-only access; Opus review had Read/Glob/Grep only. That tool difference prevents a clean model-only causal comparison. Opus's builder and reviewer were separate fresh sessions, not a linked production workflow.

The three comparison concerns were:

- ISSUE-040: restart permission described as a requirement to finish, reversing a proposal's meaning. Both reviewers missed it.
- ISSUE-045: procedure/deadline insufficiently explicit in the explanation; some details were already quoted. This is a less severe completeness concern, not a wrong category. Both missed it.
- ISSUE-048: final **configuration** change narrowed to final **policy** change. Sol caught it; Opus missed it.

These are comparison findings, not an independently adjudicated exhaustive gold set. Reassess severity rather than treating a score of three as unquestionable.

Opus's builder inserted `...` into five exact quotations. Its own checker accepted fragments separated by ellipses, weakening the stated contract, so the self-check passed incorrectly. There was also a timing-subject wording concern in ISSUE-015. A trusted contract-derived quote checker could expose the mechanical defects; it would not solve semantic verification.

Sources: [Sol diagnostic](benchmarks/prose-migration/results-sol-review-2026-09-10.md), [Opus diagnostics](benchmarks/prose-migration/results-opus-pair-2026-09-10.md). No paid repair or automatic effort escalation followed these diagnostics. Neither demonstrated a cheaper accuracy-preserving replacement.

## Questions for the audit

1. **Acceptance:** Are the semantic findings valid and proportionately important under the actual contract? Do not equate all omissions with meaning reversals. Look for additional errors and false-positive findings.
2. **Comparison boundary:** Which costs end with accepted work, and which end with an uncorrected attempt or review report? We still lack fully corrected A/C costs on the prose task.
3. **Verification ownership:** Can our latest policy avoid duplicate review without accepting confident but incomplete reviews? Full file coverage did not prevent misses. Cheap review remains a candidate to qualify, not a proven substitute.
4. **Checker independence:** Can a small trusted checker enforce mechanical requirements before submission, without exposing gold answers? Workers must not weaken it. Check our grader and mutant coverage too.
5. **Context and cost:** Verify actual source reads, parent re-entry, inherited instructions, worker configuration and cache use from receipts. Do not infer cost from model names or output tokens alone.
6. **Experimental validity:** One run per cell, synthetic/formulaic sources, uncontrolled sampling/cache state, different review tools and model-based evaluation limit generalization. Skill and no-skill configurations also differ in tool exposure. These are not isolated estimates of the cost of one policy sentence.
7. **Operational bloat:** Retain useful decision guidance without making small solo tasks load an essay. Any smaller entrypoint or verification change needs a new measured condition; do not overwrite historical policy snapshots.

Our defensible conclusion is narrow: **we have not yet demonstrated cheaper accepted work from delegation in these comparisons**. This does not prove agents always cost more, Luna is inherently inaccurate, or stronger workers cannot help. Luna independently handled the scope detail that solo Astra missed.

## Repeating the experiment within the Claude skill

Use a small script and isolated local checkouts, not a new orchestration framework. Existing fixtures and graders are reusable, but the runners contain Codex-specific settings, frozen hashes and local paths; do not run them unchanged and call it a Claude experiment.

1. Inspect the current Claude policy and actual runtime support. Freeze one Claude orchestrator model/effort, allowed Claude worker configurations, permissions, task, skill snapshot, acceptance criteria and pricing basis. Do not silently substitute models or carry over Codex's worker allowlist.
2. Prepare three matched conditions: **A**, solo without the deployment skill and with delegation disabled; **B**, no deployment skill but the same workers/tools available; **C**, current Claude deployment skill with those same workers/tools. Verify inherited instructions do not leak the skill into A/B. Keep the orchestrator fixed.
3. Give each a fresh identical starting state. Keep evaluator material, gold and previous reports outside participant context. Use native Claude delegation when testing native Claude skill behavior; our Codex-to-Claude wrapper tests do not establish that behavior.
4. If C stays solo, report that result. A separately labeled **D** may require one worker to test the delegation mechanism; it cannot be reported as spontaneous routing success.
5. Preflight the grader through the actual sandbox and permissions route using a reference and failing mutants. Put any participant-visible mechanical checker in all compared conditions; keep gold labels and semantic findings external. Freeze its assertions.
6. Set explicit bounded spending/termination rules and no automatic retries. A timeout is partial work, not success. If measuring accepted-result cost, predefine how repairs are requested and charged consistently in every arm, rather than correcting only the favored condition after seeing results.
7. Preserve original submissions, commands, source/policy hashes and raw usage receipts. Count parent and every child, cache creation/read, reasoning/output, helpers, corrections, review and integration. Report experiment preparation and independent evaluation separately. Never present API equivalents as subscription allowance.
8. Evaluate mechanical and semantic accuracy separately. Blind evaluation to condition where feasible. The old prose corpus can be a regression fixture; use a fresh held-out task for stronger claims after reading this report. Run a small matched pilot first, then repeated/counterbalanced trials within an agreed budget before recommending a policy generally.

For Claude accounting, our receipts expose uncached input, cache creation and cache read as **separate buckets**. Codex's recorded total input includes cached input. Reasoning/thinking output is already included in output. Avoid double counting. Include provider-reported helper models: the Opus diagnostics included small Haiku costs. Task traces verified Opus, but Low effort was requested rather than independently confirmed by the receipt.

Deliver: an evidence-backed audit; proposed compact Claude operational edits with their rationale kept in docs; a bounded trial plan; and, after authorized execution, results showing whole-workflow cost, acceptance, actual routing, limitations and links to immutable receipts. Negative results are useful. Do not optimize the benchmark by relaxing the user's correctness requirement.

## Local evidence and reproduction notes

Public scripts and reports are under `docs/benchmarks/`. For the latest corpus, `TASK.md` defines the contract, `grade.py` performs external checks, and `cases.json` contains **source plus author gold**: never supply that file to participants. `experiment.py`, `forced_luna.py`, `review_only.py` and `opus_pair.py` record the successive designs. Existing run guards prevent duplicate paid sessions; do not remove them to rerun an old condition.

The ignored `docs/benchmarks/prose-migration/local-fixture.json` points to the private temporary experiment root. Its `run-plan.json`, `accounting.json`, `forced-luna/`, `sol-review/` and `opus-pair/` retain manifests and receipts. Native session identifiers and further receipt locations are in each linked result report. Temporary artifacts are not durable backups; preserve needed evidence privately before any cleanup. Do not publish raw personal session logs or authentication material.

The prose corpus SHA-256 is `9ce6813ce7c9537675567e45b6ea608374af881a0e3f89187a571cc9aef699f4`; starting Git tree is `ea69aff75fedc78f6707dfbcb834e4aa4ff465f0`. The A/C/D frozen core hash is `32fad0645a3fdaf6f1c9973f558ccbeab195838575ca0a3b4af849456fe5646c`, not a claim about the current edited core. The normalized initial Luna answer used by both reviewers hashes to `8842b97ada5925862d1b88d5c934199286e3c237168c0096edd8560697610d1f`.

Recorded runtimes were Codex CLI 0.153.4 and Claude Code 2.1.266. Opus jobs used existing first-party subscription authentication, five-minute caching and disabled skill discovery/settings sources/configured MCP servers, while retaining the default Claude coding prompt. The wrapper is not an OS sandbox. Verify current runtime behavior before adapting; do not change global authentication, billing, permissions or settings merely to reproduce a test.
