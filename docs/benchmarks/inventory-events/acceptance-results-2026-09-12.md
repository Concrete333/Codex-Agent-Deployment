# Separate acceptance costs: Luna retains the saving

Both fresh Astra High reviewers accepted their supplied implementation without
findings, uncertainties or edits. Combining each saved implementation's measured
cost with its own fresh review gives **$0.544691 for Luna versus $1.047038 for
Astra solo: 47.98% lower**. This is a retrospective implementation-plus-review
comparison, not a newly executed uninterrupted pipeline or a general savings rate.

## Matched cost comparison

| Configuration | Implementation | Fresh Astra High review | Combined |
|---|---:|---:|---:|
| Astra High solo implementation | $0.775724 | $0.271314 | $1.047038 |
| Luna Max component owner | $0.042757 | $0.501934 | $0.544691 |

The Luna implementation's original $0.732967 advantage absorbed a $0.230620
review premium, leaving **$0.502347**. All values are historical API-equivalent
estimates from reconciled native usage, not actual bills, current prices or
subscription-allowance measurements. Setup, prior reviews and later adjudication
are separate below, not silently included or treated as free.

As a sensitivity check, Luna plus its review is still 29.78% below the Astra
implementation alone ($0.775724). This is arithmetic, not a second matched
experiment: it assumes no separate acceptance cost for the solo implementation.

## What the reviewers did

The [frozen protocol](acceptance-protocol.md) used two fresh contexts at Astra
High, the same prompt, schema, native controls, read-only sandbox and 1,200-second
limit. Author model names, original arm IDs, prices and previous review verdicts
were not supplied. Randomized opaque labels put the Luna submission first
(case-1), then the Astra submission (case-2). One randomized order is not
counterbalancing and cannot eliminate order/cache effects.

| Review metric | Luna submission | Astra submission |
|---|---:|---:|
| Responses | 4 | 3 |
| Input tokens, including cache | 64,316 | 45,959 |
| Cached input tokens | 24,064 | 24,064 |
| Output tokens, including reasoning | 1,507 | 566 |
| Reasoning output tokens (subset) | 129 | 158 |
| Tool calls | 3 | 2 |

Both listed files, then read the contract/evidence, all implementation modules,
protected projection/exports, public tests and added tests. All three grouped
reads per review returned successfully without truncation. Thus coverage is
supported by tool evidence, not only the final coverage array.

The Luna-submission reviewer additionally ran an in-memory, read-only probe for
staged rollback after release/ship/transfer, exact iterator-exception propagation,
preview/replay/sequence behavior, receipt/snapshot isolation, exact identities,
large integers and API dispatch. It passed. The Astra-submission reviewer reused
the supplied evidence and inspected source without another probe. This accounts
for the extra response and probe output, but does not prove which source property
caused that review choice. The Astra submission actually had more supplied test
text, so raw reading volume alone does not explain the review-price difference.

Neither reran unchanged suites, spawned children, edited code or asked for a
correction. Their handoff-related concerns were resolved by the saved host
receipts. The originals had passed 21 independent/public checks apiece, plus
15 added tests for Astra and 5 for Luna; those results remain tied to the same
source bytes.

## Adjudication and integrity

The original orchestrator checked the final reports and actual tool calls/results,
revalidated original checked receipts and the complete copied-checkout hashes,
and confirmed no active shared ownership claim. Both accept decisions stand.
No new finding required source re-investigation or correction; the previous full
source review remains valid because its artifacts are unchanged.

The benchmark-only Astra reviewer exception is exhausted after these two calls.
No production worker allowlist or skill instruction was changed. A clean/clean
pair does not measure defect-detection recall or qualify a cheaper reviewer.

## Research costs remain separate

| Recorded component | Cost |
|---|---:|
| Original two implementations | $0.818481 |
| Original fixture/harness setup turn | $3.127038 |
| Sol High fixture audit | $0.2327288 |
| Previous joint review, now observed through completion | $1.725672 |
| Separate-review setup turn, observed through completion | $1.753652 |
| Both new reviews | $0.773248 |
| Current adjudication snapshot, four completed responses | $0.963318 |
| Recorded research subtotal | **$9.3941378** |

The current snapshot ends at `2026-09-12T18:34:38.166Z`; later analysis/reporting
and final delivery are not included. Prior reusable-harness research, intervening
planning-only turns and machine costs are also excluded. This is not a final
bill. The completed previous joint-review figure replaces its earlier partial
snapshot for research accounting; it is not charged again to both configurations.
Exact setup/review turn identities and original traces are retained privately.

The research needed to measure half a dollar of per-task savings cost much more
than half a dollar. That is distinct from the repeatable execution path, but
must not be hidden when reporting this work.

## Implication and next measurement

This provides task-specific evidence for one cheap component owner, host-managed
execution and one bounded acceptance review. Review still accounts for 92.15%
of the Luna path's measured combined cost. Cutting that review without testing
its error detection would put accuracy at risk; extra role gates or live-model
waiting would spend the observed margin.

Do not rewrite the skill on one result. The next useful validation is an
uninterrupted frozen replication with fresh implementations, separately metered
reviews and no model-owned waiting, recording failures and all required
corrections. No new attempt was started during this adjudication.

Private evidence: local-acceptance.json points to inventory-review-aabe40e0,
containing randomized mapping, frozen protocol, prompts, copied sources, original
review receipts, reconciled accounting and adjudication-accounting.json. These
results supplement rather than overwrite the original inventory comparison.
