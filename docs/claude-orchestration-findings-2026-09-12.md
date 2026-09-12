# Codex orchestration findings for the Claude team

12 September 2026. Source: the working tree at `C:\Users\cwbec\Codex-Agent-Deployment`.

This consolidates the findings and corrections across our collaboration, with detail on the latest search, component-ownership and acceptance experiments. It is maintenance evidence, not deployment-time context. Several linked artifacts are still uncommitted: GitHub may not contain this working state.

Later real-task follow-up: [CCU target-selection audit](ccu-target-selection-delegation-audit-2026-09-12.md). It recovers usage, attributes several corrections to the worker itself, and identifies excessive search output and shared integration ownership. It is not a solo/team cost comparison.

**Evaluation material follows.** Do not give this report, prior conversations, reference implementations, hidden graders or earlier answers to benchmark participants. Fresh sessions must receive only their assigned task and permitted evidence. This handoff does not authorize paid runs or changes to the Claude skill.

## Bottom line

We have demonstrated a cheaper fixed-routing workflow on specified components: one inexpensive worker owns implementation and development tests, software handles execution and checks, and a capable acceptance session reviews the result. We have not demonstrated that the skill reliably chooses that workflow itself, or that delegation generally beats ordinary solo work.

Our latest uninterrupted inventory pipeline produced these results:

| Path | Implementation | Separate Astra High acceptance | Combined |
|---|---:|---:|---:|
| Astra High implementation | $0.559570 | $0.262714 | $0.822284 |
| Luna Max component owner | $0.057812 | $0.537090 | $0.594902 |

Both passed the same 21 public/independent test methods, their added tests and read-only acceptance, without corrections. Under matched separate review, Luna saved **27.65%**. But Luna plus review cost **6.31% more than Astra implementation alone**. Do not add an unnecessary reviewer to the solo baseline to manufacture a saving.

Acceptance was 90.28% of the Luna path. The next important question is whether extra review improves required accuracy enough to justify its cost—not whether we can shave another cent from Luna. [Full pipeline results](benchmarks/inventory-events/pipeline-results-2026-09-12.md).

## How to read the money and accuracy claims

All dollars are reconciled **historical API-equivalent estimates**, not invoices, current prices or subscription-allowance measurements. They use each experiment's retained rates and recorded model usage. Cached input is included in Codex total input; reasoning is included in output. Neither is an additional token bucket to charge twice. Claude accounting has separate cache-creation/read buckets and may include helper-model usage.

Execution tables include the named sessions, their tool recovery and development self-checking. Setup, fixture construction, research supervision and later adjudication are reported separately where measured. Interrupted attempts may omit in-flight usage; a snapshot is a lower bound, not a completed total. Do not add successive snapshots of the same turn together.

“Accepted” means accepted against the frozen task and available independent evidence, not proof of all possible correctness. Fresh sessions on a repeatedly used fixture are not a new held-out task. Most comparisons have one run per cell, fixed order and uncontrolled sampling/cache state. Percentages are observations, not confidence intervals or universal model rankings.

## 1. Earlier tests: why cheap workers initially failed to save

The [initial audit handoff](claude-audit-and-benchmark-handoff-2026-09-10.md) contains the detailed early methods. Its policy descriptions and semantic-finding counts are historical; use the corrections below.

| Experiment | Observed result | What it established |
|---|---|---|
| cattrs feature | Solo $1.436838; unguided delegation $2.452440; skill plus Luna at least $3.021813, timed out | A $0.051451 worker did not offset a $2.970362 coordinator. Passing saved code did not make the timed-out workflow complete. |
| Revised-skill three-task comparison | Solo total $1.326736; skill $1.653674; all skill participants stayed solo | 24.6% higher recorded cost, but no test of worker effectiveness. A large corpus could be handled with a script. |
| Prose migration | Solo $1.299660; optional-delegation arm stayed solo at $1.325202; forced Luna path $1.6628482 | The coordinator reread the complete corpus and answer. Delegation displaced writing, not expensive substantive verification. Solo was not repaired to equal acceptance, so this is not an equally accepted-result comparison. |

The cattrs and prose traces did **not** show busy polling as the explanation. Waiting overhead is real in other runs, but cannot be used to explain every expensive team.

Sol High and Opus 5 Low prose-review diagnostics did not qualify a cheaper replacement. Later audit also showed that our proposed three-finding gold set was not dependable: ISSUE-048 was misclassified, and severity needed reassessment. Do not repeat old reviewer “out of three” counts as settled accuracy measurements. The quote checker could verify literal text without verifying meaning; a blanket ellipsis ban would itself reject valid source text. [Partner correction](claude-reply-to-codex-2026-09-10.md).

The useful operational lesson survived: resolve worker-flagged judgment calls against the source. Forwarding an uncertainty is not verification. Distinguish mechanical conformance, consequential defects and unsettled requirements.

## 2. Adapter ownership and moving waiting into software

Giving one Luna Max worker the complete six-adapter component, shared parser, tests and corrections finally reduced execution cost:

| Frozen pair | Astra High solo | Astra coordinator + Luna | Observed reduction |
|---|---:|---:|---:|
| First | $1.099710 | $0.89779328 | 18.4% |
| Repeat | $1.383602 | $1.23928416 | 10.4% |

All four passed the original 226 cases. A later 150,000-character CSV probe exposed a defect in **both first-pair submissions and the reference**. Both repeat submissions passed. The first pair's unmeasured repair must not be assumed free or its original passing score described as complete correctness. The later fixture was strengthened. These were forced-routing tests, not spontaneous skill decisions. [Adapter handoff](claude-adapter-benchmark-handoff-2026-09-10.md).

The subsequent host-managed adapter replication cost **$0.894435**, against one native-delegation baseline of **$1.160008**: 22.9% lower. It passed 146 visible and 98 held-out cases plus three new regression tests after acceptance. However, Astra **implemented a CSV fix during acceptance**. Its $0.758178 acceptance session is a mixed review-and-repair cost, not directly comparable with a read-only reviewer. The first accepted host attempt cost $1.000728; recorded host spending including an earlier failed attempt was $1.980020, with possible missing interrupted usage. [Host replication](benchmarks/runner-comparison/results-host-pipeline-replication-2026-09-11.md).

Reference behavior must be checked, but is not final authority. In the related Claude exchange, the XML-whitespace claim concerned an unsettled clause; the deep-JSON `RecursionError` versus specified `ValueError` issue remained a reference/contract discrepancy. Neither should silently become a successful planted-defect detection. The later Codex malformed-CSV finding was supported by a probe distinguishing the submission from the reference and native baseline.

## 3. Search guidance: useful narrow result, failed implementation transfer

We tested a short assignment paragraph: discover relevant candidate files before reading bodies, read matching ranges, recover missing relevant output after truncation, and widen scope when coverage requires it.

The first trial was runtime-compromised. Windows shell commands started at `C:\` despite the requested checkout; another path-validation failure prevented the hashing fallback. We retained those costs and stopped the incomplete experiment. We then added actual sandbox shell-cwd qualification and corrected the scoped hash fallback before repeating. We did not weaken global sandbox protections. [Original trial and fixes](benchmarks/context-scope/results-2026-09-12.md).

The clean replication used four fresh Luna Max sessions on a source-only snapshot: 238 files, 7.7 MB, 88 production Python files. An independent AST checker required every literal settings `.get(...)` expression with exact path, line and expression.

| Search task | Existing packet | With search paragraph | Reduction |
|---|---:|---:|---:|
| Fees: 14 required matches | $0.02762 | $0.02198 | 20.4% |
| Funding: 3 required matches | $0.02548 | $0.01790 | 29.7% |
| Combined, rounded | $0.05310 | $0.03988 | 24.9% |

All four passed. Tool-output characters fell 26.4%, total input only 4.7%; cache mix explains part of the price difference. Responses were 21 per condition in aggregate. This was exact syntax retrieval, not semantic financial analysis, with no model acceptance included. [Replication](benchmarks/context-scope/replication-results-2026-09-12.md).

We then tried the same paragraph on a settled reservation component, keeping Luna Max and whole-component ownership fixed:

| Reservation pair | Assignment only | With paragraph | Treatment saving |
|---|---:|---:|---:|
| Original | $0.03897336 | $0.03376816 | 13.36% |
| Frozen repeat | $0.03868776 | $0.03353020 | 13.33% |
| Unattended repeat | $0.04262936 | $0.05292576 | -24.15% |
| Total | $0.12029048 | $0.12022412 | 0.055% |

All six passed 16 public/independent methods, including subcases and a 100-operation sequence, plus added tests and source acceptance. No correction worker was needed. The apparent 13% implementation advantage disappeared. The third treatment used more input and output; there was no truncation or compaction to explain away. Order was treatment-first throughout. [Unattended results](benchmarks/reservation-component/unattended-results-2026-09-12.md).

We retained the paragraph for repository-search assignments, not a general implementation-cost claim. We have not measured a saving from shorter policy text, compaction avoidance or a new model ladder.

## 4. Inventory: separating implementation from acceptance

The larger synthetic inventory component covers receive, hold, release, ship and transfer; exact tenant/SKU/hold identities; partial holds; event-ID replay; atomic batch rollback; sequence state; isolated receipts/snapshots; dry-run preview; and API validation. It is standard-library, single-process code—not a concurrency, persistence or network benchmark.

Each owner received the same settled contract, stubs, example and three editable modules, with optional development tests. The external suite has four public and 17 independent methods, validation subcases and a 450-event lifecycle/replay exercise. Correct and valid-alias references passed; the starter and eight mutants failed. A pre-freeze Sol High fixture audit strengthened rollback, iterator failure, invalid preview, replay-field and receipt-isolation coverage. [Fixture audit](benchmarks/inventory-events/fixture-audit-2026-09-12.md).

We fixed implementation routing to Astra High solo versus one Luna Max owner. Separate Astra High reviewer calls were **explicit benchmark-only exceptions**, not a production worker-policy change.

| Comparison | Astra implementation | Its review | Total | Luna implementation | Its review | Total | Reduction |
|---|---:|---:|---:|---:|---:|---:|---:|
| Saved implementations + fresh separate acceptance | $0.775724 | $0.271314 | $1.047038 | $0.042757 | $0.501934 | $0.544691 | 47.98% |
| Fresh uninterrupted host pipeline | $0.559570 | $0.262714 | $0.822284 | $0.057812 | $0.537090 | $0.594902 | 27.65% |

These are two designs on one fixture, not a pooled savings estimate. The first reused unchanged implementations already reviewed jointly; its new review price was retrospective. The second automatically ran fresh implementations and then fresh acceptance in one batch. All implementations passed; reviewers returned no findings or uncertainties and made no edits. No correction loop was exercised. [Original implementations](benchmarks/inventory-events/results-2026-09-12.md), [separate acceptance](benchmarks/inventory-events/acceptance-results-2026-09-12.md), [fresh pipeline](benchmarks/inventory-events/pipeline-results-2026-09-12.md).

Reviewers had identical prompts, configuration and tools, opaque labels, no author/cost/prior-verdict metadata, and enforced read-only checkouts. Actual reads and full checkout hashes were verified. Implementation order was solo then Luna; randomized review labels happened to put Luna first in both comparisons. This is not counterbalancing.

In the fresh run, Astra added 10 tests and Luna five; all passed. The Luna-submission review took an extra context-reading turn and ran a targeted in-memory rollback/iterator probe. That passed. The solo-submission review inspected source and existing evidence without a new probe. This documents additional review work, not proof that Luna code inherently requires twice the review.

Luna implementation used 561,568 input and 27,542 output tokens, versus Astra's 79,222 and 5,715. **The saving is dollars, not tokens.** The review premium consumed much of the worker advantage. The stronger earlier result—Luna plus review cheaper even than solo implementation without extra review—did not replicate.

## 5. Runtime, verification and accounting lessons to reuse

- **Let software own waiting and mechanical transitions.** The latest host batch ran implementations, gates and reviewers without a paid coordinating model waiting between stages. Prefer native completion events when sufficient; do not create model polling or scheduled check-ins as a substitute.
- **Preflight the actual runtime route before spending.** A successful absolute-path grader does not prove shell cwd is correct. Check interpreter identity, checkout access, read-only enforcement and artifact hashing through the same sandbox route the participant will use.
- **Gate acceptance on complete, validated evidence.** Process exit and a `status` key alone are insufficient. Validate the full handoff, artifact identity/scope, protected files and check receipts. Preserve original records; stop on partial/blocked/uncertain ownership. Do not auto-retry or pay for acceptance of an empty submission.
- **One owner for dependent work.** Keep implementation, development tests and corrections together. Use one substantive acceptance owner. The root checks evidence, integrity and unresolved findings instead of automatically rereading everything after a completed review.
- **Keep review read-only if comparing reviewer prices.** Route any measured correction to its designated owner and charge all repair/review rounds. Label older sessions that mixed these roles honestly.
- **Qualify the checker, not just the code.** We found both missed defects and invalid tests: the reservation fixture originally rejected a valid import-alias implementation. Audit references and mutants before freezing; record later discoveries without rewriting historical results.
- **Separate ambiguous requirements from defects.** Preserve judgment calls in handoffs. Require an explicit contract basis or decisive evidence before prescribing a correction. A reference match cannot excuse a clear contract violation; an unsettled clause cannot establish one.

Research overhead is substantial. The latest four execution sessions totaled **$1.417186**; completed setup added **$1.552672**, and an adjudication snapshot added **$1.034902**. The recorded replication subtotal was therefore **at least $4.004760**, excluding later reporting and previous fixture/harness work. Earlier live-supervision snapshots included setup, reading, accounting and review—not just polling. Do not label all parent input “wasted waits.”

## 6. What should change—and what should not

The supported workflow is a candidate for **settled components with qualified, affordable checks**, where the coordinator actually relinquishes implementation. Small deterministic work still belongs in a script; tightly coupled reasoning may belong with the original capable owner.

Keep operational instructions short and actionable. Keep this report and benchmark data outside ordinary skill context. The recent inventory results do not justify new routing mandates, more reviewers, or relaxed acceptance. The Codex production allowlist remains Luna, Terra, Sol and Opus 5, with Luna Max only; the benchmark Astra reviewer exceptions do not carry forward. Claude should retain its own independently justified configuration policy.

We still lack evidence for:

- reliable spontaneous delegation that saves accepted-result cost;
- a whole-current-skill advantage over no skill or unguided delegation;
- a generally adequate cheaper reviewer;
- accuracy-preserving removal of independent review on consequential tasks;
- robust gains across unseen tasks, repeated orders and failure/correction paths;
- converting these dollar estimates into subscription-allowance savings.

## 7. Most useful next Claude-side experiment

First isolate **the marginal value of acceptance**. Use a new coding task with clearly consequential contract-settled defects and clean controls. Hide the defect count, author and prior findings. Score misses, false alarms, uncertainty handling and final behavior—not just whether a reviewer produced findings. Freeze the suite before participant runs; include valid alternative implementations so strictness is not mistaken for accuracy.

For cost, compare a capable solo owner with a cheaper whole-component owner under the review requirements genuinely needed for the task. Report both implementation-only and implementation-plus-required-acceptance totals. Keep the reviewer fixed before testing a cheaper reviewer. If repairs are permitted, freeze the same bounded repair policy and charge all failed attempts and rechecks.

Repeat and counterbalance within an agreed budget. Do not change prompt, routing, permissions and checker simultaneously. After qualifying the mechanism, add an optional-routing arm to test whether the skill actually recognizes when delegation is worthwhile. A forced cheap-worker success cannot answer that question.

The inventory fixture can provide a cross-vendor replication, but it is now familiar to both teams. Use fresh isolated participants, and call it a replication rather than unseen-task validation. Adapt the provider execution/accounting layer; do not transplant GPT prices or infer Claude configuration quality from these results.

## Reproduction and audit map

- Research background: [coordination references](agent-coordination-references.md), [captured model comparison](model-performance-comparison.md). These support hypotheses, not task-level cost guarantees. Earlier benchmark-metric corrections are summarized in the [initial handoff](claude-audit-and-benchmark-handoff-2026-09-10.md).
- Operational mechanism: [delegation guide](../references/delegation.md), [software runner guide](../references/software-runner.md), [runner](../scripts/deployment_runner.py), [hash helper](../scripts/deployment_hash.py).
- Inventory materials: [contract](benchmarks/inventory-events/task/SPEC.md), [grader](benchmarks/inventory-events/grade.py), [evaluator-only reference](benchmarks/inventory-events/reference.py), [implementation driver](benchmarks/inventory-events/experiment.py), [acceptance driver](benchmarks/inventory-events/acceptance_pair.py), [pipeline driver](benchmarks/inventory-events/pipeline.py), [frozen protocol](benchmarks/inventory-events/pipeline-protocol.md).
- Private evidence under `C:\Users\cwbec\AgentDeploymentBenchmarks`: `inventory-2f64dd2f` (original), `inventory-review-aabe40e0` (retrospective reviews), `inventory-9776fff9` and `inventory-review-c8048fd2` (fresh pipeline). The ignored local pointer files in the fixture directory identify original receipts, manifests, traces, accounting and separate adjudication records.

Existing drivers retain exclusive-start guards and completed experiment identities. Do not remove guards or reuse an old run as a fresh attempt. Create and freeze a separately authorized experiment. This report itself launched no model tests, changed no operational policy and was not committed or pushed.
