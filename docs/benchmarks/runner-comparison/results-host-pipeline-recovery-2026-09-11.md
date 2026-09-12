# Host-run Luna and fresh Astra acceptance: accepted after offline recovery

The second host-pipeline attempt reached acceptance for **$1.000728** in captured API-equivalent model cost. Its final implementation passes all 146 visible cases, all 98 held-out cases and five new regression tests. This is 13.7% below the saved native-delegation baseline, or 6.4% below when the earlier timeout's captured cost is included.

This was **not an uninterrupted pipeline success**. Luna completed, but host-side hashing failed on a sandbox-created file. After an offline runtime fix, the same submission was revalidated and its previously unstarted Astra acceptance session ran once. No additional worker was called. Research repair/supervision costs are excluded, as in the earlier experiments.

## Cost and outcome

| Arm | Worker | Coordinator / acceptance | Total | Final checks |
| --- | ---: | ---: | ---: | --- |
| Saved native Astra High + Luna Max | $0.110186 | $1.049822 | $1.160008 | 244 frozen cases; five post-hoc regressions pass |
| Saved software recovery, live Astra High | $0.097023 | $2.102332 | $2.199355 | 244 frozen cases; five post-hoc regressions pass |
| Host-run Luna Max, fresh Astra High acceptance | $0.070984 | $0.929744 | $1.000728 | 244 frozen cases; five regression tests pass |

The new pipeline plus its earlier timed-out attempt totals **$1.085584** in captured cost. The timeout may omit in-flight usage. Earlier costs from developing and testing the different live-coordinator software arm are not included in that subtotal; they remain in their own reports. None of these figures are subscription allowance consumption or actual bills.

Acceptance/corrections account for 92.9% of this run's cost. The difference from the native baseline includes both lower coordinator cost and a different worker sample; it cannot all be attributed causally to waiting behavior. The new run is 54.5% cheaper than the saved live-coordinator software arm, whose repeated waits were previously measured separately.

## Frozen comparison and recovery

Attempt 02 used fresh stubs and a predeclared 1,800-second Luna Max safety limit instead of 900 seconds. The acceptance limit remained 1,200 seconds. Preparation verified both model prompts and the coordinator command matched attempt 01 after checkout-path substitution. Models, efforts, task, policy snapshot, ownership, final checks and substantive acceptance requirements were unchanged. Participants received no previous solution, external grading results or planted-defect guidance.

Luna finished in 755.371 seconds with a complete structured handoff and process exit 0. The runner then failed before its final checks because the host could not read the new `imports/adapters/_shared.py`. The independent read-only sandbox grader could read it and passed all 244 cases. The original blocked receipt was preserved.

The compatibility fix hashes declared files inside the same **read-only Codex sandbox** if host access is denied. It changes no ACLs, imports no checkout code and launches no model. Paths are checked against the checkout, returned hash coverage is validated, and failures still block acceptance. Offline revalidation checked the original request identity, complete handoff, stopped worker, nine protected files, unchanged required artifact hashes, all handoff-listed files and the same declared final check. A separate recovery receipt records those observations.

Only after revalidation did a fresh Astra High coordinator start. It used the already-frozen acceptance prompt and command, with the same bounded handoff/check packet format. Its session lasted 185.61 seconds. No model coordinator existed during worker execution. This is a fixed host workflow, not autonomous model routing; specification construction is fixed harness input rather than measured model planning.

## What acceptance found

The worker's code already passed the entire frozen suite. Astra identified one reference-confirmed CSV defect and made a second XML change whose behavior conflicts with the reference and requires adjudication. Astra itself implemented both changes; the $0.929744 is review, corrections and rechecking combined, not read-only reviewer cost:

- Both CSV adapters accepted stray quotes in unquoted fields. The task explicitly rejects malformed CSV quoting. The shared parser gained stricter quote validation.
- The XML adapter rejected literal `DOCTYPE` text inside memo CDATA. Astra interpreted the contract's prohibition of declarations as distinct from that text as memo data, and changed the parser accordingly. The reference also rejects these inputs: this remains an open reference/contract discrepancy, not a confirmed accuracy gain or automatically a false alarm.

Five regression tests initially produced four failing and four erroring subcases, then passed after the changes. They cover malformed quotes, valid quoted/unquoted memo preservation, literal declaration-like CDATA, rejection of actual declarations, and mixed entity/CDATA memo content. Postflight confirmed that only `_shared.py` and `statement_xml.py` changed from the worker handoff; a new regression test file was added. All nine runner-protected files remain unchanged.

The same five tests were then run read-only against the saved native and live-software submissions; both passed. A subsequent reference check passed the CSV expectations and actual-DOCTYPE rejection but failed four CDATA-related subcases. These are **post-hoc, reviewer-written probes**, not new independent held-out validation; the XML expectations are disputed against the reference. They do not establish general reviewer accuracy or absence of other defects. The frozen suite was not modified.

## Accounting and verification

| Configuration | Recorded responses | Input | Cached input | Output | Reasoning output, included in output |
| --- | ---: | ---: | ---: | ---: | ---: |
| Luna Max | 28 | 872,317 | 802,048 | 34,074 | 20,513 |
| Astra High | 13 | 274,417 | 225,664 | 4,331 | 1,006 |

Effective models/efforts were confirmed from rollout turn contexts. Own-thread response usage reconciles to recorded totals. Astra made no delegation calls or worker-wait calls; implementation, acceptance and local corrections are included. Host preflight, offline repair, research supervision and external grading are excluded consistently with earlier results.

All 97 offline repository tests pass. The runner, hashing helper and operational guide were synchronized to the installed skill. Benchmark claims remain in docs, not the operational skill. The worker and acceptance processes stopped; the held ownership claim was explicitly released without modifying the original receipt.

## Interpretation and next step

The external-driver shape can produce an accepted result at lower captured model cost than this native baseline, including the previous timeout. The saving is modest and requires replication. It does not yet establish that the skill beats solo work or unguided delegation, nor that the repaired pipeline succeeds unattended on a fresh run.

Repeat the now-repaired pipeline unchanged before changing reviewer models or policy text. Acceptance dominated cost, but the CSV correction was reference-confirmed; do not remove verification merely to lower the bill. Qualify cheaper reviewers separately on unseen defects and clean controls, adjudicating reference/contract conflicts before scoring them.

## Evidence

The ignored `local-fixture.json` locates `host-pipeline-02/` and `acceptance-recovery/`. They retain original and recovery receipts, frozen hashes, prompts/commands, process/event logs, before/after grades, reconciled accounting and `postflight.json` with exact failing regression output and post-hoc controls. `recover_acceptance.py` performs one guarded acceptance continuation; `audit_acceptance.py` performs no model calls.

Worker session: `01a090e6-d794-71b0-9f41-982804484424`. Acceptance session: `01a090f7-186d-7aa3-915b-3f88d868367b`. The original attempt and exclusive start markers are preserved.
