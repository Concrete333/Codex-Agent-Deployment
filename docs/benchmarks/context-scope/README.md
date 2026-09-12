# Search-scope instruction: worker-packet ablation

**Status: stopped; comparison inconclusive.** Three workers completed; the fourth
was safety-aborted after a Windows shell cwd failure was identified. Do not use
the costs as evidence for changing the skill. See [results](results-2026-09-12.md).

This tests a proposed addition to the delegation assignment, not a complete new
skill or spontaneous model routing. Both arms use Luna Max through the existing
software runner, with identical tools, corpus, task contract, output schema and
objective acceptance. A has the existing bounded assignment pattern. B appends:

> Context handling: Discover candidate files within the relevant paths and file types before reading bodies; exclude unrelated generated or captured content. Read matching functions or ranges. If output truncates, recover the missing relevant ranges instead of treating the partial return as complete. Widen the search when evidence or coverage requires it.

The corpus freezes 238 files (7,700,300 bytes) from the current Spaceships project:
root Python/JavaScript source and top-level Python/JavaScript tests. It includes
no databases, credentials, profiles, raw captures or historical plans. Files are
copied privately, not committed here. Application modules must not be executed.

Two tasks inventory literal `.get(...)` reads of named settings in production
Python, reporting path, source line, key and the complete call expression. The
fee/economic set has 14 matching calls; the smaller funding set has three. Neither
matching count is supplied to participants. This is syntax-level completeness,
not a test of economic interpretation, implementation or financial correctness.

## Frozen procedure

- Planned order: fees A then B; funding B then A. One fresh worker session per
  cell, four sessions total (each may make multiple model requests).
- Each worker has 900 seconds; no automatic retries or evaluator-fed repairs.
- The worker may use scripts and self-checks. The host executes the final grader.
- Acceptance requires the exact complete inventory without duplicate/wrong rows,
  unchanged source hashes and protected task/instruction/hash-manifest files.
- The offline AST oracle passes the correct inventories and rejects empty,
  omitted, duplicated, wrong-expression and wrong-location variants before
  spending. Its acceptance command is also preflighted in the actual sandbox.
- Answers are compared as multisets of path/line/key/parsed expression. Whitespace
  is immaterial; quoting an unrelated line or the key alone cannot pass.
- Freeze all code, both assignments, source, oracle data, baseline delegation
  guide and candidate instruction. Preserve original receipts and exclusive
  start markers. Do not silently rerun cells or change the intervention mid-pair.

The first offline preflight encountered a Windows read restriction on an
out-of-checkout answer file. No model was launched. The final grader derives its
oracle from the protected source inside the checkout; the external script and
protected corpus-hash manifest remain fixed. Host-side frozen answers separately
qualify the grader. This does not grant workers access to sibling trials.

## Measurement and scope

Reconcile native own-session model/effort and per-response usage. Report input,
cached input, output, responses, compaction and large/truncated read evidence.
Use the existing frozen historical rates in `revision-ab/summarize.py` only as
API-equivalent accounting, not current prices, actual bills or subscription
allowance. Missing telemetry is unknown, not zero.

There is no model coordinator in the measured workflow. Research preparation,
this supervising conversation and external grading are excluded. This isolates
whether the extra worker instruction changes retrieval behavior and accepted
worker cost. It does not measure whether a live orchestrator passes it correctly,
whether delegation beats solo work, or whether compaction-heavy implementation
gets cheaper. Counterbalanced task order does not control cache state or model
sampling. A positive result still needs replication; a null or negative result
does not justify inflating the operational skill.

Potential later tests, not authorized as part of this four-cell invocation:
resume an interrupted implementation from a compact checkpoint versus broad
rediscovery; compare retained component ownership on a caller/mock-boundary
change. Keep independent acceptance and model settings fixed. Do not combine
these interventions with this retrieval test.

## Run

`python docs/benchmarks/context-scope/experiment.py prepare` is offline.
`... experiment.py run` launches the four guarded cells sequentially.
`... experiment.py summarize` reuses saved results and native usage.

The existing cells must not be rerun or relabelled. A future comparison needs a
new fixture, a passing shell-cwd preflight and a new frozen manifest; the runner
was repaired after these cells stopped.

Private locations are recorded in ignored `local-fixture.json`. The runner uses
the previously established shared state directory and stops on unresolved
ownership. No live Spaceships files or global Codex settings are changed.

The underlying non-interactive CLI provides JSON execution output and structured
results; see [official documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
Local runner compatibility and authentication are checked before worker launch.

## Fresh replication

The fresh four-cell comparison completed: all exact checks passed, with lower
recorded worker cost in both guided arms. See [replication results and limits](replication-results-2026-09-12.md).

`replicate.py prepare` copies the original frozen corpus into new isolated
checkouts under the local benchmark directory. It does not copy worker answers
or refresh the source project. All four actual shell working directories and
both sandbox graders must pass before the new manifest is saved. The repaired
runner repeats its preflight immediately before each worker launch.

`replicate.py run` starts the four new sessions in the same A/B, B/A order and
stops on a blocked runner or uncertain ownership. It never reruns the aborted
experiment's identities. `replicate.py summarize` and `measure_replication.py`
read saved evidence without model calls. Private location: ignored
`local-replication.json`.

The hypothesis, treatment paragraph, model/effort, source, objective contracts
and checker remain unchanged. Runtime repairs and checkout placement differ
from the aborted experiment, so compare arms within this replication, not costs
across the two experiments. This remains one run per task/arm, not a statistical
estimate or an implementation benchmark.
