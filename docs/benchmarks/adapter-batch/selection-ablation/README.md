# Conditional model-guide loading: matched skill comparison

Test one change: when the worker model and effort are already fixed within the
allowed configurations, skip the model-selection guide. Preserve ownership,
verification, recovery, waiting and model restrictions.

[Completed results](results-2026-09-10.md): both passed all 244 cases. Conditional
loading removed 847 policy words, but total API-equivalent cost rose from $0.62
to $0.96 in this pair, including an additional review-driven correction.

| Public condition | Internal plan arm | Skill | Actual required workflow |
| --- | --- | --- | --- |
| Old policy | A | Frozen first-pair policy | Astra High + exactly one Luna Max |
| Conditional read | C | Updated entrypoint, identical references | Astra High + exactly one Luna Max |

Both invoke the existing runner's internal C workflow. **There is no solo arm.**
Use the outer run-plan arm to distinguish them, not the runner's result arm.
Each child uses `fork_turns="none"`, owns all six adapters, tests and corrections;
the coordinator retains acceptance. No other workers or nested delegation.

## Strengthened fixture, version two

The original 140 visible and 86 held-out cases remain. Six generated visible
cases add large fields in both CSV formats, embedded/final bare CR in fixed-width
memos and valid large numbers in ignored pending/posted JSON fields. Large inputs
are constructed by a compact public module, not stored as huge visible fixtures.
Twelve additional held-out cases vary the CSV lengths at/beyond the former limit,
include malformed long quotes, and vary CR placement and nested ignored numbers.
The complete checker now covers **146 visible + 98 held-out = 244 cases**.

The copied reference's two CSV adapters use a local unbounded strict parser;
the version-one reference is unchanged. The new reference passes qualification,
while the reintroduced standard-library field limit fails. Existing wrong-sign,
dropped/reordered-record, memo-trimming, swallowed-error, tampering and stub
mutations also fail. Reference grading passes through the actual read-only sandbox.
One offline preflight initially called the old grader; that path was corrected
before inference, and its failed receipt was retained.

Expected cases are generated without calling reference implementations. Hidden
generators and reference code stay outside participant checkouts. As before,
separation is instruction-constrained rather than adversarial filesystem isolation.
Both new conditions receive the same strengthened source and task. Their costs
must not be treated as a matched comparison with the old fixture's solo costs.

## Frozen design and measures

Run one old-policy/conditional-read pair sequentially, old first, in fresh
checkouts. Keep Astra High, worker availability, prompts and 1,200-second process
safety limits identical. No automatic retries or evaluator hints. Check the actual
worker model/effort, spawn count, guide-loading behavior, acceptance and own-thread
parent/child usage. A cheaper failed or incomplete run is not a saving. A run that
still loads the guide does not demonstrate the intended context reduction.

Before inference, verify that the policy snapshots differ only in the entrypoint's
conditional-loading instruction, and participant prompts match apart from checkout
paths. Freeze scripts, source, both policies, reference, held-out cases and runner.
Inspect outcome and code without changing grading or feeding back repairs.

Use the established API-equivalent accounting, including parent and child input,
cache, output, review and corrections; reasoning is included in output. Research
preparation, supervision and external grading are excluded, not claimed free.
Subscription usage is not measured. Cache state and sampling are not controlled;
one pair cannot establish a causal cost effect or general routing quality.

`experiment.py prepare` creates a separate private fixture;
`experiment.py preflight` qualifies it without model calls;
`experiment.py run` launches the guarded paid pair;
`reporting/summarize.py` reconciles local receipts. The reused driver's
`experiment.py summarize` shortcut has a relative-path error in this nested
directory; the offline adapter uses the original accounting library without
modifying frozen trial code, rates or receipts. The ignored
`local-fixture.json` locates those receipts. Do not delete run guards or overwrite
the earlier adapter experiments.
