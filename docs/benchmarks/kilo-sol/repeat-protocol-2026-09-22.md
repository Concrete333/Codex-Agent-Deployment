# Fresh three-arm repeat

Run once each, in the frozen seeded order **solo, Luna, MiMo**:

1. Sol High implements and verifies alone.
2. Sol High prepares one assignment, Luna Max implements, then the same Sol
   session resumes for acceptance and any local corrections.
3. Sol High prepares one assignment, uncapped MiMo-V2.6-Pro thinking implements
   through Kilo, then the same Sol session resumes for acceptance/repair.

All are fresh sessions and checkouts. Neither previous baseline nor previous
worker solution is reused. The six-adapter task is retained, with the CSV quote
grammar clarified explicitly. A quote in an unquoted field must raise
`ValueError`; quoted doubled quotes must decode correctly.

## Frozen measurement improvements

- **254 cases:** 150 visible and 104 held-out. Added four visible quote cases
  and six held-out variants, including valid controls. These are regression
  variants of a known issue, not a new unseen task. Gold reference passes;
  a permissive CSV mutant specifically fails both visible bare-quote cases.
- **Identical starting source and scope:** hash-checked inputs, protected files,
  pinned LF checkout behavior, six adapters plus optional helper and one test file.
- **Common coordinator guidance:** both delegated arms load the same deployment
  skill and assignment/review reference. Only worker identity/transport differs
  in preparation; Kilo's routing skill is not additional coordinator context.
  This measures the host-managed route, not automatic skill selection.
- **Common result format:** solo completion, worker handoff and resumed
  acceptance have the same status/summary/files/checks/judgments/blockers schema.
- **Same timeouts:** 30 minutes per model stage, no worker iteration cap, one
  worker attempt per delegated arm. Completed failed/partial work may be repaired
  by Sol within its acceptance stage. Unresolved ownership stops the pipeline.
- **Pre-registered order and prices:** seed 20260922 selects solo/Luna/MiMo;
  versions, order, per-million pricing rates, prompts and runtime hashes are
  saved before any paid call. The order happened to match the requested listing;
  one order cannot remove temporal/cache/provider variability.
- **Stage evidence:** retain CLI stdout/stderr, session IDs, terminal receipts,
  worker artifacts, pre-review grading and final grading. Private grading is
  not passed to the models. No after-grading model repair is included as a pass.
- **Host-managed waiting:** scripts block, not model turns. One completion
  notification follows batch termination; no repeated model polling.

## Analysis rules

Count all task-model usage: Sol preparation, worker attempts, resumed review,
integration and corrections. Deduplicate response usage and reconcile cumulative
resume totals; never add a cumulative acceptance event to preparation again.
Use recorded model/effort and frozen rate assumptions. Count Kilo's reported
cost separately; retain unknown values rather than replacing them with zero.

Report pass/failure alongside cost. A failed submission's spend is attempt cost,
not cost to an accepted result. Compare worker and final files to identify actual
repair. Separate elapsed time, raw token volume and price-weighted estimates;
none measures subscription allowance. Test counts are coverage, not complete
proof of accuracy. Setup, harness work, supervision and analysis are research
overhead and remain excluded from task-execution figures, explicitly.

This is one fresh run per condition, not a statistical replication set. Compare
the new arms primarily with each other; do not pool the earlier 244-case results
as identical trials. CLI scaffolds and inherited Kilo tool configuration still
differ; no claim that the worker model alone explains an outcome is warranted.

Implementation reuses `experiment.py`, `luna.py`, `uncapped.py`, the established
grader and accounting code. `repeat.py prepare` qualifies and freezes; `run`
performs the paid batch. The ignored `local-repeat.json` locates local evidence.
