# Full pipeline replication: saving holds under matched review

Both fresh implementations passed the 21 frozen checks and their separate Astra
High reviews, with no findings, corrections or retries. The original orchestrator
adjudicated both accept decisions after inspecting review execution evidence and
revalidating source/receipt hashes.

**Luna implementation plus review cost $0.594902; Astra implementation plus
review cost $0.822284. The saving was $0.227382, or 27.65%.** Unlike the previous
retrospective comparison, these four sessions ran automatically in one host batch,
without a coordinating model waiting between implementation and review.

## Costs and accuracy

| Configuration | Implementation | Separate Astra High review | Combined |
|---|---:|---:|---:|
| Astra High solo | $0.559570 | $0.262714 | $0.822284 |
| Luna Max component owner | $0.057812 | $0.537090 | $0.594902 |

These are reconciled historical API-equivalent execution costs, not current API
prices, actual bills or Codex allowance consumption. Research setup and this
adjudication are separate below.

Both implementations passed 21 independent/public methods. Astra added 10 tests,
Luna 5; all passed. Actual model/effort matched the frozen settings. The component
owner kept implementation and development tests together. No reviewer wrote code
or called another agent; all four attempts completed without a correction phase.
Normal development self-checking is included in implementation costs.

| Usage | Astra implementation | Luna implementation | Review of Astra | Review of Luna |
|---|---:|---:|---:|---:|
| Responses | 5 | 18 | 3 | 5 |
| Input, including cache | 79,222 | 561,568 | 45,054 | 82,219 |
| Cached input | 57,600 | 486,400 | 24,064 | 38,400 |
| Output, including reasoning | 5,715 | 27,542 | 575 | 1,210 |

The Luna path saved dollars, not tokens. Its review was $0.274376 more expensive
than the solo submission's review and accounts for 90.28% of its combined cost.
The review of Luna used an additional context-reading turn and an in-memory
probe of iterator failure after partial hold mutations, including dry-run,
replay, sequence and snapshot isolation. That probe passed. The review of Astra
used source inspection and saved checks without a new probe. These observations
explain extra review work, not a causal model-quality ranking.

## Important sensitivity: does solo need another review?

If the Astra solo implementation is accepted without a separate reviewer, its
measured cost is $0.559570. Luna plus review is then **$0.035332 more expensive
(6.31%)**. In the previous saved-submission comparison Luna plus review was
cheaper even under that assumption; that stronger result did not replicate.

The matched experiment deliberately requires separate acceptance for both arms.
Do not use it to justify adding a reviewer to solo work merely to make delegation
look cheaper. The unresolved decision is whether an extra review materially
improves required accuracy on the real task. This clean/clean fixture cannot
establish that. It also does not show that a cheaper reviewer is adequate.

## Integrity and method

The [pipeline protocol](pipeline-protocol.md) reused the task, grader, reference,
implementation requests and review prompt/settings. Original-byte checks and
request-equivalence checks passed before spending. Correct and alias reference
variants passed; the starter and eight mutants failed as expected. Fourteen
offline host-control tests passed. No new paid fixture audit was commissioned.

Order was Astra implementation then Luna implementation. Review labels were
randomized once; they again placed Luna first, then Astra. Fresh isolated copies
hid explicit author/model/cost and prior-verdict metadata. This single order
does not control model randomness or cache/order effects. The reviewers received
current artifacts and check evidence, not earlier answers or acceptance reports.

Actual tool outputs confirm successful, untruncated reads of the contract,
evidence, all implementation modules, protected projection/exports, and public/
added tests. The passing targeted probe is retained in the Luna-review trace.
There were no findings or unresolved uncertainties requiring root to repeat
the source review. Pending-host-check notes in the solo handoff are resolved by
saved host receipts and the completed review.

Original submission receipts and complete reviewer checkout file sets/hashes
were revalidated during adjudication. No active ownership claim remains. The
root did not rerun unchanged tests or perform another implementation. Original
automated receipts are preserved, with final adjudication recorded separately.

## Research overhead

| Recorded component | Cost |
|---|---:|
| Four execution sessions combined | $1.417186 |
| This replication's completed setup/launch turn | $1.552672 |
| Current adjudication snapshot, four completed responses | $1.034902 |
| Recorded replication subtotal | **$4.004760** |

The adjudication snapshot ends at `2026-09-12T19:14:50.409Z` and omits later
reporting and final delivery. Previous fixture construction/audit/harness research
and machine costs are outside this subtotal, not free. The automatic preparation
of review packets in the host is not another paid model setup turn. Setup and
adjudication are not arbitrarily divided between configurations.

## What this supports

The cheaper component-owner path retained a saving with equivalent separate
review: 47.98% in the saved-implementation comparison, 27.65% in this fresh batch.
Those are two observations with different execution designs on one synthetic
task, not a pooled general savings rate or a whole-skill/no-skill experiment.
Fixed routing, settled requirements, host-managed execution and qualified checks
remain important boundaries. Failure recovery was not exercised.

No skill changes follow automatically. Keep the existing ownership and verification
guidance; do not turn this into a blanket mandate to delegate or add reviews.
Before relaxing verification or claiming savings over ordinary solo work, test
the accuracy benefit of additional review on consequential held-out defects and
clean controls. Broader task replication remains necessary.

Private evidence: local-pipeline.json points to inventory-9776fff9, whose
review-pointer.json points to inventory-review-c8048fd2. Original receipts,
pipeline-accounting.json, pipeline-adjudication-accounting.json and tool traces
remain preserved. No new paid call was started during this adjudication.
