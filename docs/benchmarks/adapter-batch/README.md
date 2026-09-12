# Adapter batch: solo versus one required worker

The [first matched pair](results-2026-09-10.md) and its
[frozen repeat](results-replication-02-2026-09-10.md) passed all frozen cases, with
18.4% and 10.4% lower API-equivalent cost for required delegation. An additional
large-CSV probe exposed a gap in the reference and first pair; the repeat pair
passed it. These trials do not measure the skill's decision to delegate.

This diagnostic asks whether a cheap worker can own substantial, specified
implementation and its corrections while the coordinator verifies economically.
It does **not** measure the skill's spontaneous choice to delegate.

| Condition | Coordinator | Worker |
| --- | --- | --- |
| A: solo | Astra High; no deployment skill | Disabled |
| D: forced delegation | Astra High using the frozen skill | Exactly one Luna Max, minimal inherited context |

The existing runner retains internal arm `C` for D; results must label it D.
No Terra, Sol, Astra, Fable or Claude trial workers are authorized. One Sol High
agent prepares the scaffold/reference independently of the main agent's test
cases; that is research preparation, not a measured participant.

## Task

Implement six transaction import adapters: bank CSV, European debit/credit CSV,
status-filtered JSONL, structural XML, fixed-width records and nested JSON batches.
One working canonical adapter and common normalization helpers establish the
interface. Parsers still have distinct field mapping, parsing and failure rules.
The API is wired already; each adapter and optional shared parsing file belong
to one owner. No network, package installation or architecture change is needed.

Both conditions receive the same contract, stubs, working example and 140
independent visible cases (60 valid, 80 invalid). External grading additionally
uses 86 held-out cases (80 valid, six duplicate-ID failures), generated before
the trials. Fixtures exercise signs, decimal precision, escaping, Unicode, date
validity, header validation, JSON duplicate keys/non-standard numbers, XML scope,
record order, empty inputs, skipped events and duplicate emitted IDs.

Scripts and automation remain available to both conditions. The test does not
inflate work with irrelevant files or prohibit efficient solo scripting. It is
nevertheless a purpose-built synthetic package, not a public production benchmark.

## Acceptance and controls

Require all visible and held-out cases, protected-file integrity, permitted edit
scope and any added tests to pass. Inspect implementation for hardcoding and
untested contract failures; counts alone are not proof of correctness. The task
does not demand extra review stages or a particular implementation technique.

Qualification occurs before model trials: a separate reference must pass; stubs
and mutations for wrong sign, dropped records, reversed order, altered memo,
swallowed errors and checker tampering must fail. Run reference grading through
the actual read-only sandbox and inspect effective prompt isolation before launch.

Both participants can inspect and execute the supplied checker. It is protected,
and external evaluation uses the canonical copy outside their write scope.
Reference implementations, held-out cases, other results and personal context
are excluded from participant assignments. This is instruction-constrained
access, not adversarial filesystem isolation.

Freeze the task, fixture generator, all cases, reference, skill and runner before
execution. Run A then D sequentially in fresh checkouts, same Astra High and
1,200-second safety limit, no automatic retries or evaluator-fed repairs. Writers
can make corrections within their original run. A timeout or failed acceptance
is reported, not repaired after scoring and called a win. The process limit is
not a dollar or subscription-allowance cap. No billing or global settings change.

D adds a short requirement to use one Luna Max worker for the whole adapter
batch, with `fork_turns="none"`. The coordinator retains final acceptance and
may not launch additional workers. Verify actual spawn/model/effort in telemetry;
failure to follow the required arrangement invalidates the intended mechanism
comparison, even if code passes. There is no optional-delegation arm in this pair.

## Accounting and interpretation

Count the coordinator and every descendant, including cached input, reasoning
within output, corrections, review and waiting re-entries. Use the retained
standard API-equivalent rates from `revision-ab/summarize.py`; do not interpret
them as subscription charges or allowance. Preparation, supervising the research
and external evaluation are separately excluded from participant totals.

Compare accuracy and completed-workflow cost together. A cheaper failed attempt
is not a saving. Successful results would justify replication and then a separate
optional-routing test, not a general claim that agents save money. There is one
run per condition, no controlled sampling/cache state and no representative task
sample. Prior task costs are not a matched baseline for this new task.

## Reproduction

Use `prepare.py`, then `experiment.py preflight` (no model calls). Only
`experiment.py run` launches the paid pair; an exclusive marker prevents silent
reruns. `experiment.py summarize` reuses the prior own-thread usage reconciliation.
The pilot runner and prior experiments remain unchanged; a frozen private runner
snapshot restricts workers and appends the forced-delegation directive.

Public task sources, fixture generation, reference and grading code are retained
here. Do not give this entire directory to participants. The ignored
`local-fixture.json` points to unique private temp locations for the source copy,
gold reference, held-out cases, policy snapshot, preflight and trial receipts.
Raw sessions and authentication material must not be published.

For the authorized second pair, `replication/repeat.py prepare` qualifies the
same frozen inputs and creates separate `replication-02` receipts under the
private fixture root. `replication/repeat.py run` launches one guarded A/D pair;
`replication/repeat.py summarize` reconciles its usage. The original fixture
pointer, trial receipts, runner, skill and grading cases remain unchanged.
Do not remove a started marker to silently repeat a paid run.
