# Checked-component diagnostic

[Results — 10 September 2026](results-2026-09-10.md).

One sequential A/C pair tests a short skill entrypoint and independently supplied
acceptance checks on the existing idempotency component. Delegation is optional.
This is a new condition, not a replacement for any earlier receipt.

| Arm | Coordinator | Workers | Policy |
| --- | --- | --- | --- |
| A | Astra High | Disabled | No deployment skill |
| C | Astra High | Native Luna, Terra or Sol; at most one active child | Revised skill; Luna Max only |

Claude is excluded from this pair to avoid sharing its usage with a concurrent
Claude-specific experiment. No Astra or Fable workers are authorized. If C stays
solo, report routing and solo overhead; do not claim worker effectiveness. There
is no unguided B arm, so policy text and delegation-tool exposure remain confounded.

## Task and checker

Preparation reuses `revision-ab/component/task` without supplying a solution.
The task now explicitly permits inspection and execution of `check_contract.py`
and protects that checker and its hash manifest. Both arms get the same task,
public tests, independent visible assertions and initial implementation stub.

The checker retains 28 prior behavior tests and one integrity check, then adds
five tests for huge-integer TTL/clock combinations, nested payload subclasses,
post-return mutation of a handler-retained payload, and keyed service use without
a ledger. There are 34 checker methods plus six existing public tests. A huge-TTL
test also checks conflicts while unexpired. These checks are not a proof over
every input; TTL/clock subclass interpretation and general numeric rounding are
not separately adjudicated by this pilot.

The new private reference corrects overflow rejection for valid finite inputs;
the old reference and tests remain frozen. The reference passes, and receipt
aliasing, exclusive expiry, overflow rejection and checker-tampering mutants
fail. The reference also passes through the actual read-only sandbox route.
Prompt preflight suppresses personal skill discovery. A Sol High read-only
checker audit was preparation overhead, not a measured participant.

External grading first compares protected files, including the supplied checker
and its manifest, then runs the canonical checker outside the participant's
write scope and discovers public/added tests. Each invocation is a fresh process.
The reference implementation and evaluator material are not placed in trial
checkouts. Instruction boundaries are not adversarial filesystem containment.
Inspect submitted code for untested contract gaps as well as reporting test counts.

## Bounds and interpretation

Two runs only, A then C, each with a 1,200-second process safety limit; no automatic
retry, evaluator-fed repair, forced delegation or test-time skill change. A failed
attempt is not an accepted result. Workers can perform their own corrections
within the original run. The time limit is not a dollar or subscription-allowance
cap. No API key, billing or global configuration changes are made.

Freeze task, checker, runtime configuration and policy hashes before execution.
Record actual model/effort, parent and child usage, cache counters, completion,
scope integrity and external checks. Retain raw receipts privately. Whole-trial
API-equivalent estimates include workers and in-run review/correction, but exclude
experiment preparation, supervision and external evaluation; report those
boundaries explicitly. The accounting helper retains the previous frozen rate
basis for comparability, not a new claim about current subscription pricing.

The corpus, checker exposure and policy differ from the earlier component runs.
Only this matched pair compares those configurations. One run per cell cannot
establish a reliable savings rate or prove a specific instruction caused the result.
The independent-checker emphasis follows [official evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
to define task-specific criteria and test failures; it does not make our fixtures representative.

## Reproduce

`prepare.py` creates a new private temporary fixture; `experiment.py preflight`
qualifies it without inference. `experiment.py run` starts the paid pair once,
guarded by an exclusive marker. `experiment.py summarize` reconciles usage.
Run from the repository root with the prepared Python interpreter. Do not delete
run guards or overwrite frozen receipts to repeat a condition.

The ignored `local-fixture.json` locates `preflight.json`, `run-plan.json`, task
copies, the policy snapshot and accounting under system temp. The original runner
is reused through a private snapshot changing only worker availability and child
concurrency. Runtime defaults are Codex CLI 0.153.4 and the prepared Python 3.13.
