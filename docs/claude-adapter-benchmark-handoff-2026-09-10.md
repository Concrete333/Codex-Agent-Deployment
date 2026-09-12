# Claude audit handoff: the two lower-cost adapter trials

Prepared 10 September 2026 for the agent maintaining
`C:\Users\cwbec\Claude-Agent-Deployment`. Source repository:
`C:\Users\cwbec\Codex-Agent-Deployment`.

This updates the adapter-test findings, not the full history in the
[earlier handoff](claude-audit-and-benchmark-handoff-2026-09-10.md).
Use it for audit and experiment design. **It reveals evaluation answers:** do not
pass it, this conversation, reference solutions or previous results to benchmark
participants. Use fresh isolated participant sessions. This handoff does not
authorize new paid runs, unlimited retries or edits to the Claude skill.

## Bottom line

Two forced-delegation workflows cost less than Astra High solo on the same
specified implementation task, including coordinator review and worker corrections.
The second pair repeated the frozen setup; no policy optimization was introduced.

| Pair | Solo total | Team coordinator | Luna worker | Team total | Saving |
| --- | ---: | ---: | ---: | ---: | ---: |
| First | $1.099710 | $0.820628 | $0.07716528 | $0.89779328 | 18.4% |
| Frozen repeat | $1.383602 | $1.126462 | $0.11282216 | $1.23928416 | 10.4% |

Combined spending: **$2.483312 solo versus $2.13707744 team, 13.9% lower**.
This is a descriptive aggregate of two runs per condition, not a general savings
estimate. All four submissions passed 226 frozen external cases. Subsequent probes
found a contract defect in both first-pair submissions and the reference; both
repeat submissions passed those probes. Do not claim full correctness for the
first pair or include an unmeasured later repair in its cost.

## Task and experimental design

Implement six transaction-import adapters: bank CSV, European debit/credit CSV,
status-filtered JSONL, structural XML, fixed-width records and nested JSON batches.
Output is a normalized record list with exact integer amounts, valid dates,
preserved memos, source ordering and duplicate-ID rejection. Invalid input must
raise `ValueError`. The contract, wired API, common helpers, working example and
stubs were supplied. Standard library only; no network or architecture redesign.

One owner implemented the whole batch, its shared parser, tests and corrections.
There were no six-way teams or separate implementer/test-writer handoffs. This was
a synthetic, specified task with cheap executable checks—not a production benchmark.

- **A:** `gpt-6-astra`, `high`; no deployment skill; delegation disabled.
- **D:** same coordinator with the frozen skill; exactly one `gpt-5.6-luna`,
  `max`, `fork_turns="none"`, required to own the complete implementation batch.
  The runner calls this arm `C` internally; reports call it **D**.
- Both pairs ran A then D in fresh checkouts, using Codex 0.153.4 and a 1,200-second
  safety limit per run. No automatic retries, evaluator hints or repairs after
  scoring. All four runs completed normally. Time was not the optimization target.
- Personal context and skill discovery were suppressed. The D coordinator read
  the 324-word skill, 918-word delegation guide and 858-word model-selection guide.
  A 41-word directive required the worker. Effective model/effort and actual spawn
  were verified in telemetry; no nested, replacement, Astra or Claude workers.
- Inputs, policy, reference and runner were frozen and checked afterward. Repeat
  prompts matched the first pair apart from fresh checkout paths. Original receipts
  and frozen inputs remain intact.

The design tests whether a required cheap-worker workflow can save money. It does
**not** test the skill's decision to delegate, its advantage over unguided
delegation, or which worker model is best.

## Verification and what it caught

Independent visible fixtures contained **140 cases: 60 valid, 80 invalid**.
Held-out fixtures contained **86 cases: 80 valid, six duplicate-ID failures**.
External grading used the canonical checker outside participant write scope,
checked protected-file integrity and edit scope, and ran any added tests.
Separate reference qualification and deliberately broken implementations tested
wrong signs, dropped/reordered records, altered memos, swallowed errors and checker
tampering. Participants were instruction-isolated, not adversarially filesystem-isolated.

The coordinator reviewed the source rather than accepting the worker's test report:

- **First pair:** it caught rejection of a bare CR inside a fixed-width memo and
  rejection of a valid large JSON number (`1e999`) in an ignored pending-event field.
  Luna corrected both. The visible checker had missed both.
- **Repeat:** it independently caught the standard CSV reader's 131,072-character
  field limit, absent from the contract. Luna replaced the limited reader and added
  long-field tests. Astra rechecked the changed parser and ran **1,200 generated CSV
  writer round trips**. Those checks and corrections are included in team cost.

The repeat solo implementation also independently covered large CSV fields.
That inspired an external post-hoc probe: a 150,000-character memo containing
quotes and CRLF, tested in both CSV formats. The unchanged probe was run against
the reference and all four saved submissions. The reference and first pair failed
both cases; the repeat pair passed both. Neither active participant received the
probe or its results. Original frozen scores were not rewritten.

**The reference and frozen checker have a known coverage gap.** Before a strengthened
Claude trial, create a new fixture version, correct and requalify the reference,
and include these long-field, bare-CR and ignored-number cases. Keep old artifacts
unchanged. Preserve an independent held-out component rather than handing every
discovered answer to a participant. Passing a reference is not proof that the
reference fully implements the contract.

## Economics and coordination findings

Costs are API-equivalent estimates, **not API invoices, Codex allowance or Claude
subscription usage**. Retained per-million-token rates: Astra $10 uncached input /
$1 cached / $50 output; Luna $0.20 / $0.02 / $1.20. Own-thread response records were
deduplicated and reconciled, including all descendants. Cached tokens are part of
input; reasoning tokens are part of output. Neither should be counted twice.

Shared research preparation, supervision and external grading were excluded and
not measured here. Preparation included an independent Sol High reference/scaffold
author and supervisor-authored fixtures. Both arms received the prepared artifacts.
This does not establish the economics of first creating specifications and checks
for a new real-world task.

The teams used **4.96x and 8.79x more input tokens** than solo. Savings came from
placing much of the output generation on the cheaper model, not from reducing
total tokens. In the repeat, Astra generated 3,191 output tokens versus 9,099 solo;
Luna generated 37,529. Astra's reduced output cost outweighed its extra input cost
and the worker bill. Cache state varied and was not controlled.

The coordinator still represented about 91% of team cost. Both coordinators read
the implementation, but did not write a competing solution or take over repairs.
Both reused the same worker for one correction round and made two long native
wait calls under the 25-minute configuration. No short polling loop occurred.

## Implications for the Claude agent

1. Transfer the workflow hypothesis, **not the GPT model assignments or prices**:
   a capable fixed coordinator can delegate a settled component through checks
   and corrections, while retaining substantive verification and acceptance.
2. Keep review. It found real defects in both trials, and savings survived that
   review. These results do not justify a cheaper reviewer, spot-check replacement
   or removal of source inspection.
3. Deterministic round-trip checks are a useful candidate for extending coverage
   without large model-visible output. Their isolated cost benefit was not measured.
4. A small context-reduction candidate is skipping model selection when model and
   effort are already fixed. Both coordinators unnecessarily loaded the 858-word
   selection guide. This is **unimplemented and untested**, not a proven saving.
5. After qualifying a new fixture version, hold the Claude coordinator fixed and
   compare solo with one explicitly configured allowed cheaper worker. Confirm
   actual worker use; an all-solo pair cannot test worker economics. Use Claude's
   own telemetry and prices, including its cache categories, and adapt the runner
   rather than invoking the Codex-specific runner unchanged.
6. Then test optional routing and other tasks. Two same-order forced pairs, without
   controlled sampling/cache state, cannot establish general model superiority or
   the value of the skill itself.

## Follow-up after this handoff

The proposed conditional model-guide loading change has since been implemented
and tested against the old policy on a requalified 244-case fixture. Both teams
passed. The updated policy read 847 fewer policy words but cost $0.96 versus
$0.62, with a review-driven JSONL correction. The earlier recommendation's
"unimplemented and untested" status applied when this handoff was written;
see the [follow-up results](benchmarks/adapter-batch/selection-ablation/results-2026-09-10.md)
before treating that candidate as a demonstrated saving.

## Evidence and current state

Read these selectively; do not load the entire benchmark collection:

- [First pair: costs, usage and corrections](benchmarks/adapter-batch/results-2026-09-10.md).
- [Repeat: costs, usage, coverage gap and receipt IDs](benchmarks/adapter-batch/results-replication-02-2026-09-10.md).
- [Protocol and reproduction](benchmarks/adapter-batch/README.md).
- [Participant contract](benchmarks/adapter-batch/task/TASK.md),
  [case generator](benchmarks/adapter-batch/make_cases.py),
  [external grader](benchmarks/adapter-batch/grade.py),
  [reference directory](benchmarks/adapter-batch/reference/).
- [Post-hoc large-CSV probe](benchmarks/adapter-batch/replication/probe_large_csv.py).
- [Own-thread cost accounting](benchmarks/revision-ab/summarize.py).

The ignored `docs/benchmarks/adapter-batch/local-fixture.json` locates private
receipts; repeat receipts live under `replication-02`. Raw sessions remain local.
No operational policy changed during either successful pair; the core SHA-256 is
`11649c2374f14adf97437ccaaacfcd6935d3b0a3fbc71d8f6fcbae849755f02d`.
At writing, repository HEAD is `c095231`, with the recent benchmark directory and
other work still uncommitted. Audit the local working tree, not just GitHub.
