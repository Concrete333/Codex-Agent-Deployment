# Inventory events: solo owner versus one component worker

[Results — 12 September 2026](results-2026-09-12.md): both accepted without
corrections. Luna implementation cost $0.042757 versus Astra solo $0.775724.
Joint acceptance cost was captured separately; per-arm end-to-end savings
remain unmeasured.

[Separate acceptance comparison](acceptance-results-2026-09-12.md): fresh Astra
High reviews accepted both saved implementations. Implementation plus its own
review cost $0.544691 for Luna versus $1.047038 for Astra solo (47.98% less).
This retrospective comparison excludes separately reported research overhead;
it is not yet an uninterrupted pipeline replication.

[Fresh full-pipeline replication](pipeline-results-2026-09-12.md): both accepted
without corrections. Luna plus review cost $0.594902 versus Astra plus review
$0.822284 (27.65% less). Without a separate solo review, Luna's reviewed path
would instead cost 6.31% more. Research overhead is reported separately.

Test whether a cheap component owner plus acceptance costs less than a capable
solo implementation under the same correctness requirements. New synthetic
task; no prior participant solutions or tests are supplied. It is larger in
behavioral scope than the reservation fixture: five event operations, holds,
global replay identities, transactional batches, sequence receipts and snapshots.
It is not a production project or a representative sample of coding tasks.

| Arm | Implementation | Final acceptance |
|---|---|---|
| Solo | Fresh standalone Astra High; deployment skill and delegation absent | Original Astra High task, read-only |
| Worker | One Luna Max via the existing host runner | Same original task, same requirements, read-only |

The solo baseline is an experimental standalone owner, not an Astra worker
authorized by the skill. Production model restrictions are unchanged. Both
arms use identical native CLI controls, source, short assignment, structured
handoff, tools, Python and 1,800-second termination bound. No search-guidance
ablation, Claude configuration, or cheaper reviewer is combined with this test.
The skill guides this host's bounded assignment; the worker does not read policy.
This is fixed routing, not evidence that an orchestrator will choose it unaided.

One initial session per arm, solo first. No automatic retries or evaluator-fed
correction. Normal development corrections within the attempt are included.
Failed/partial results are reported, not counted as cheap accepted outcomes.
Blocked runtime or uncertain process ownership stops the batch. Time bounds
are safeguards, not a dollar or subscription cap.

## Acceptance and qualification

Four public methods and seventeen external methods cover literal outcomes,
validation subcases and a 450-event lifecycle plus replay. The reference is
used only to qualify the checker, never as the oracle for participant output.
Qualify the reference and a valid import-alias implementation; reject the
starter and eight consequential mutants before any participant call. A separate
Sol High fixture audit is preparation overhead, not a participant or reviewer.
Its five coverage findings were fixed before freezing: hold-operation rollback,
iterator sequence rollback, invalid previews, kind-specific replay conflicts and
mutation of replay receipts. No participant result informed those additions.

The written contract, tests, protected projection, exports, initial sources,
runner and frozen historical accounting rates are pinned before launch. Both
checkouts must pass the actual sandbox shell-cwd preflight. Evaluator/reference
files live outside participant checkouts and are excluded by assignment scope;
this is not an adversarial filesystem boundary.

The host retains independent results and runs added tests in the same sandbox.
It validates protected hashes, changed-file scope, handoff completeness and
artifact hashes. Passing is only ready_for_review. On user return, one read-only
acceptance review covers both complete implementations, the shared preview and
projection paths, correctness gaps and judgment calls. No reimplementation or
redundant rerun of unchanged checks. Necessary corrections require a separately
authorized continuation and count toward cost through acceptance.

## Waiting and accounting

Reuse the existing shared runner state. Software executes the pair serially in
a hidden background process. The launch turn ends after one initial check;
there is no model polling, scheduled check, new reviewer agent or notification.
Return when the private STATUS.md says ready_for_review or needs_attention.

Record actual model/effort, input/cache/output, failed attempts and corrections.
Keep implementation-only figures separate from cost through acceptance. Capture
this setup turn and Sol audit as preparation; preserve review usage separately.
If the joint review cannot be reliably split by arm, report its shared cost and
the break-even review-cost difference; do not arbitrarily halve it or claim
precise per-arm accepted costs. Public benchmark documentation and fixture
engineering are research overhead, not zero-cost production work.

This extra external source review is deliberately symmetric, but a competent
solo agent may need less independent review in normal use. Report that limit,
fixed run order, one run per arm, and historical API-equivalent pricing (not
bills or allowance). No operational skill changes during the comparison.

`experiment.py prepare` is offline; `run` starts at most two measured sessions;
`summarize` reads existing usage only. A private ignored local-fixture.json points
to checkouts, qualification, original receipts and status. A durable start guard
prevents accidental reruns. No live Spaceships files are changed.
