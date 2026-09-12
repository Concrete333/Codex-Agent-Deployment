# Native delegation versus software-managed dispatch

This paired trial tests the optional deployment runner and host bridge. Both arms use a fresh Astra High coordinator and exactly one Luna Max worker attempt on the existing version-two six-adapter task: 146 visible cases and 98 held-out cases. This is not a solo-versus-team or spontaneous-routing trial.

[First attempt: incomplete](results-2026-09-11.md). Native passed; software hit a copied-script access failure before worker launch. Use `postflight.py` for its partial accounting; do not rerun the guarded experiment or treat the failed arm as a saving.

[Authorized recovery: both pass, software costs more](results-recovery-2026-09-11.md). The repaired software arm passed all 244 cases but cost 89.6% more than the saved native baseline. Repeated outer tool waits were the largest recorded cost difference.

| Arm | Dispatch and final visible check | Substantive review |
| --- | --- | --- |
| Native | Coordinator spawns Luna with no history, waits for completion and runs the final check | Astra High |
| Software | Coordinator triggers an already-authorized host ticket; software launches Luna, waits and runs the same check | Astra High |

Both start from identical task files and receive the same frozen skill. Workers receive the same assignment and execution contract apart from checkout paths; the CLI additionally enforces its structured-output schema. Runtime-added contexts are measured, not assumed identical. In particular, the runner currently retains its own worker discovery configuration, while a native child inherits its coordinator's runtime controls.

One attempt per worker is allowed. Both coordinators may make necessary local corrections after the worker stops and must recheck affected behavior. Neither may retry, resume the worker, spawn another reviewer or change acceptance criteria. This makes the runner's current single-attempt limit explicit and equal across arms. Coordinator review and correction costs are included.

The software host request is prepared and armed by the experimental harness; request design is therefore held fixed rather than priced as an agent task. Reading the assignment, dispatching/collecting, reviewing and correcting are measured coordinator work. Harness development, research supervision, host preflight and external scoring are excluded equally and are not amortized into the result.

## Run and evidence

`python -B -X utf8 experiment.py prepare` snapshots the skill/scripts, prepares isolated checkouts, requalifies the reference and failing stubs through the actual sandbox, inspects coordinator prompt isolation and freezes source/held-out/grader/harness hashes. It calls no models. Existing fixture mutation qualification is retained by the source experiment.

`python -B -X utf8 experiment.py run` runs native then software sequentially, with a 1,200-second coordinator safety limit and 900-second software-worker limit. The native worker is bounded by the coordinator's overall limit; this asymmetry must be reported if a deadline is reached. A durable start marker prevents silent reruns. A runtime failure stops the pair; a graded accuracy failure is retained rather than repaired by the evaluator.

`python -B -X utf8 experiment.py summarize` reconciles own-thread response usage for each coordinator and worker. The external CLI worker is included explicitly because it is not a native descendant. Estimates use the prior experiment's frozen API-equivalent rates, not subscription allowance. Full prompts, launch commands, private receipts, grades and session evidence remain in the ignored local fixture directory.

Acceptance requires visible/held-out cases, protected-file integrity, permitted edit scope, added tests and substantive contract review. Tests alone do not prove semantic correctness. No held-out failures are fed back to participants. Compare failed attempts separately from accepted-result costs. One pair cannot establish a reliable saving; task representativeness, uncontrolled cache state and run-order effects remain limitations.

## Authorized software recovery

`recover_software.py prepare|run|summarize` retains the original pair and prepares one new software arm against its native baseline. The task, assignment, worker/coordinator settings, skill snapshot, deadlines and grading remain fixed. Runtime scripts use the canonical repo path. Runner and Claude-helper hashes must match the original snapshot; the host client has one access fix: check authorized endpoint identities without requiring metadata access to their ancestors. Host-side ancestry validation remains mandatory.

The first recovery preflight (`software-recovery-01`) caught that ancestor-access issue without a model call. The second (`software-recovery-02`) qualified the actual interpreter, shell, client path, private-state write denial, complete fake-worker trigger/receipt exchange and repeat receipt retrieval. Its prepared manifest pins the recovery script, runtime scripts, request, prompt and starting files before the paid call. Existing start markers and failed evidence are not removed.

This is a recovered software-only comparison, not a new uninterrupted pair. Report both the new attempt's cost and software cost including the earlier failed launch. No automatic additional paid attempt is authorized by these scripts. Use the saved outcome before deciding on another run.

## Host execution followed by fresh acceptance

[First run: worker timeout, acceptance correctly blocked](results-host-pipeline-2026-09-11.md). Saved code passes 244 cases; captured worker cost is approximately $0.085, but there is no accepted result or measured acceptance cost.

`host_pipeline.py prepare|run|summarize` tests one new arm against the saved baselines. Software runs one Luna Max attempt and the visible check, validates the handoff and current artifact/protected-file hashes, then starts a fresh Astra High coordinator for acceptance. No benchmark coordinator exists during worker execution. An invalid, partial, blocked or failed-check attempt stops before acceptance without an automatic retry. This is a fixed workflow, not an autonomous routing test.

The source fixture, model/effort settings, model-facing skill snapshot, substantive acceptance requirements and grader remain frozen. The coordinator prompt changes only for its post-worker entry point; worker/check evidence is supplied as a bounded packet. The worker execution contract additionally clarifies that handoff artifacts are relative file paths. The runner validates and hashes all claimed files as well as required artifacts. No reviewer model or tool-set change is combined with this trial.

The worker retains its 900-second safety limit; fresh acceptance has 1,200 seconds. Total allowed workflow time therefore differs from the earlier live-coordinator arms; report any deadline effect. The external held-out grader runs before and after acceptance, privately, without feeding failures back. Acceptance may make necessary local corrections and recheck them. Research supervision still costs tokens outside the measured workflow; this design removes benchmark-coordinator waits, not all experimental overhead. Specification construction is fixed harness input, not measured model planning.

An exclusive start marker prevents a second paid launch. Input/runtime hashes and the original comparison are checked before dispatch. Prompts, receipts, events, pre/post grades and reconciled accounting stay beside the existing private comparison evidence. Report the fresh run separately from earlier implementation/recovery spending. Repetition and a genuinely unseen task are still needed to establish a reliable saving.

The explicitly authorized second attempt uses `host_pipeline.py prepare|run|summarize --attempt 02`. It starts from fresh stubs with a predeclared 1,800-second worker limit; Astra High acceptance retains 1,200 seconds. Preparation asserts that both model prompts and the coordinator command match attempt 01 after checkout-path substitution. It retains the same policy, task, checks and models, and preserves the first attempt's private files and start marker. Report its cost both alone and including the captured cost of the timed-out first attempt; interrupted in-flight usage from that attempt may be missing.

[Second attempt: accepted after offline file-access recovery](results-host-pipeline-recovery-2026-09-11.md). Captured cost is $1.000728, or $1.085584 including the earlier timeout. The same completed worker was reused after sandbox-based hashing revalidation; `recover_acceptance.py` started only the previously unspent acceptance session. Both frozen suites and five new regression tests pass. This is not an uninterrupted pipeline result. `audit_acceptance.py` runs the same new tests against saved baselines without model calls or changing those submissions.

The authorized replication uses `host_pipeline.py prepare|run|summarize --attempt 03`, the repaired hashing path and fresh stubs. Both prompts and the acceptance command must match attempt 02 after path substitution; worker and acceptance limits remain 1,800 and 1,200 seconds. It adds no judgment-call field, read-only reviewer restriction, worker correction round or new test cases. Astra acceptance may still make local corrections. The XML reference discrepancy remains open and is not fed into this frozen trial.

[Replication: accepted without manual recovery](results-host-pipeline-replication-2026-09-11.md). Captured cost $0.894435; all 244 frozen cases plus three new regression tests pass. Astra corrected one reference-confirmed CSV quoting defect. Cost includes acceptance, local corrections and self-corrected shell-directory errors. This is one uninterrupted successful run, not proof of general savings or pure reviewer efficiency.
