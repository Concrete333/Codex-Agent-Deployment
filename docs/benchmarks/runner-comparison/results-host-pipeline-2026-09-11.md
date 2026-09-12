# Host-run Luna followed by fresh Astra acceptance: incomplete

The worker hit the frozen 900-second safety timeout before returning its terminal handoff. The acceptance gate stopped the pipeline, so no Astra acceptance session ran. The saved implementation passes the external grader's 146 visible and 98 held-out cases, including protected-file and edit-scope checks. This is **not an accepted-result cost or a demonstrated saving**.

| Arm | Captured API-equivalent cost | Outcome |
| --- | ---: | --- |
| Saved native Astra High + Luna Max | $1.160008 | 244 cases pass; coordinator accepted |
| Saved software recovery with live Astra High | $2.199355 | 244 cases pass; coordinator accepted |
| Host-run Luna Max, then gated fresh Astra High | $0.084857 | Worker timeout; 244 cases pass; acceptance not started |

The timeout cost covers recorded responses only; an interrupted in-flight response may be missing. Do not subtract this incomplete arm from an accepted baseline to claim a percentage saving. Earlier failed software launch cost ($0.446918) remains separate; that prior software recovery cost including its launch failure is $2.646273.

## Method

One explicitly authorized fresh worker attempt used the same version-two adapter source fixture, Luna Max, 900-second worker timeout, model-facing skill snapshot and external grader as the saved comparison. A script owned execution and the visible final check. Only a validated complete handoff with intact files and passing declared checks could start a fresh Astra High acceptance coordinator. Acceptance retained the prior substantive requirements and permission for necessary local corrections; no cheaper reviewer was substituted.

The worker prompt added one artifact-format clarification: relative file paths without descriptions. The acceptance prompt was adapted to begin after worker completion, using a bounded handoff/check packet. These changes and the fresh coordinator context mean prompts are not byte-identical to the earlier arms. Acceptance had a separately declared 1,200-second safety limit, never exercised. No model planning phase was included: the assignment was fixed harness input. This tests a fixed workflow, not spontaneous model routing.

## Observations

- Luna Max was confirmed from rollout turn context: 30 recorded responses; 1,123,008 input tokens, including 1,040,128 cached; 39,565 output tokens, including 24,586 reasoning tokens.
- Recorded usage reconciles to the last recorded thread totals. Timeout still makes any unrecorded in-flight usage unknown.
- The worker first reported two visible large-CSV-field failures, corrected them, and subsequently reported all 146 visible cases plus focused in-memory probes passing. It did not return its final handoff before termination.
- The runner marked the attempt `partial`, ran no declared final checks and started no acceptance session. The external evaluator graded the saved files afterward; its result does not replace substantive acceptance.
- No discoverable added test files were found. The worker's reported inline probes are separate from the independent frozen suite.
- Worker process-tree termination reported success. Recorded worker/runner processes and immediate children were absent at cleanup; the held ownership claim was explicitly released, preserving the original receipt. No automatic retry or continuation ran.

## Improvements implemented

The runner now validates and hashes handoff-listed files as well as required artifacts. `review_gate` rechecks completion, request identity, declared check results, protected files and current artifact hashes before a caller starts paid acceptance. Negative tests cover missing/out-of-checkout files, failed checks, changed assignments/contracts/artifacts and altered completion status. The gate accepts valid Codex and Claude receipts without treating either as accepted work.

This trial also exposed an accounting bug: a timeout lacks the completed worker metadata, so the initial experiment summary displayed zero agents and zero cost. The summarizer now recovers the session identity from the CLI event stream and refuses to report zero when a launched worker's identity is unknown. The runner likewise preserves interrupted Codex session identity without claiming complete usage or success. These accounting changes were made after the run; they did not alter its execution. All 93 offline tests pass.

The installed runner and its operational guide were synchronized with the repo. The guide distinguishes external host execution from a live coordinator merely waiting around a script. No benchmark claims were added to operational skill context.

## Next comparison

The gate prevented a wasted acceptance launch, but fresh acceptance cost remains unmeasured. The next run should predeclare a more generous worker safety timeout, appropriate to a cost-first task where speed is not an objective. Keep Astra High acceptance and the task unchanged; do not change the reviewer simultaneously. Retain this incomplete attempt and its captured cost in recovery-inclusive reporting. Do not shorten substantive verification merely to fit the wall-clock limit.

One run per cell on a repeatedly used fixture cannot establish general savings or reviewer reliability. Research setup/supervision and external evaluation are excluded consistently with the earlier experiments. Prices are the same frozen historical API-equivalent rates, not subscription allowance or actual bills.

## Evidence

Reproduction entry point: `host_pipeline.py prepare|run|summarize`. Its exclusive start marker prevents a paid rerun. The ignored `local-fixture.json` locates private evidence under `host-pipeline-01`: frozen manifest and input hashes, commands/prompts, worker receipt location, final grade, result and corrected accounting. Original evidence is retained. Worker session: `01a090d0-cb21-7903-951d-09ef726f84f7`. No acceptance session ID exists.
