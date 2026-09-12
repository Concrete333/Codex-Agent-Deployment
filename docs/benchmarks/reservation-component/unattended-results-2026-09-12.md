# Unattended reservation comparison

Both Luna Max implementations were accepted without a correction worker.
The search-guided arm cost **24.15% more** this time. Across all three pairs,
the worker costs are effectively equal; the earlier 13% advantage did not hold.
No operational skill change follows from this result.

## Worker results

| Pair | A: assignment only | B: with search guidance | B saving vs A |
|---|---:|---:|---:|
| Original | $0.03897336 | $0.03376816 | 13.36% |
| Frozen repeat | $0.03868776 | $0.03353020 | 13.33% |
| Unattended repeat | $0.04262936 | $0.05292576 | -24.15% |
| Total | $0.12029048 | $0.12022412 | 0.055% |

These are frozen historical API-equivalent estimates, not bills or Codex
allowance measurements. All attempts used Luna Max, confirmed in native usage
records; no Sol correction ran. Both arms retained component ownership.

The [unattended protocol](unattended-protocol.md) kept the task, prompts,
configuration, checks and B-first order unchanged. The host launched the workers
serially, ran checks and stopped at `ready_for_review`. The original orchestrator
ended its launch turn and returned only when the user requested acceptance.
No reviewer worker, automation or live-model polling loop was added.

| Current pair | A | B |
|---|---:|---:|
| Responses | 15 | 16 |
| Input tokens, including cache | 349,102 | 442,986 |
| Cached input tokens | 295,168 | 357,888 |
| Output tokens, including reasoning | 21,616 | 23,957 |
| Tool-output characters | 14,902 | 20,698 |

B used more input and output, not merely a more expensive cache mix. Neither
trace showed truncation or compaction. This does not establish that the added
paragraph caused the difference: sampling, cache and fixed order remain
uncontrolled. Retain useful search discipline, but withdraw a measured
implementation-cost advantage on this fixture.

## Acceptance review

The original Astra High orchestrator reviewed all three changed source files
and the added tests in each arm against the frozen contract. It revalidated
the saved receipt, protected files and artifact hashes, without rerunning
unchanged tests or editing either implementation.

- Both passed 16 independent/public test methods, including validation subcases
  and the fixed-seed 100-operation sequence. Saved added-test results: A 6/6,
  B 5/5.
- Validation and duplicate aggregation precede all stock mutation; failures
  leave stock unchanged. Tenant/SKU identities, first-occurrence order and
  iterator exception propagation are preserved.
- Preview calls the same core with `dry_run=True`. Submission stores independent
  journal rows, including for empty success. API dispatch preserves the result.
- No scope violations, artifact-list gaps or unresolved material defects.
  Worker notes that the external check was pending are resolved by host receipts.
- Shared active ownership was released. Original attempt receipts remain
  `ready_for_review`; the separate acceptance record supplies the human-facing
  final decision.

This accepts the written contract, not arbitrary callbacks, allocation failures,
concurrency or production suitability outside that contract.

## Cost through review: recorded subtotal, not a final total

| Component | Recorded API-equivalent cost |
|---|---:|
| Both workers | $0.09555512 |
| Setup/launch turn, completion event observed | $1.923442 |
| Review turn snapshot: 8 completed responses | $0.864220 |
| Recorded subtotal | **$2.88321712** |

The review snapshot stops at `2026-09-12T17:43:11.209Z`; it excludes later
responses, including report writing and final delivery. Setup is selected by
the exact turn identity saved in the manifest, not the latest conversation turn.
Original fixture development/audit and machine costs are excluded. Setup and
review are shared costs, not arbitrarily assigned to A or B.

The earlier live-supervision snapshot alone was $4.49812, also incomplete and
covering more than waiting. These unequal scopes do not establish a percentage
saving. What this run demonstrates is that host execution can finish the pair
without repeated model wakeups. Even so, setup and acceptance dwarf the roughly
ten-cent worker bill. There is still no matched solo baseline proving net savings.

## Next useful experiment

Stop repeating this tiny fixture to optimize fractions of a cent. Reuse the
host runner on a larger held-out, settled component and compare a solo owner
with one component-owning worker under equivalent acceptance requirements.
Freeze the acceptance packet and account for setup, corrections and review on
both sides. Do not introduce a cheaper reviewer or change search guidance in
that same comparison.

The ignored `local-unattended.json` points to `reservation-c2b6b91e`, containing
original receipts, checks, trace metrics, `unattended-supervision.json` and the
separate `acceptance-review.md`. No new paid attempt was launched for this review.
