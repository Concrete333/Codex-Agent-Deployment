# Saved-answer semantic review

The evaluator read every submitted explanation and supporting quotation against
the previously reviewed source. This is a coordinator/model review, not blind
human adjudication. Automated classification and citation validity are reported
separately. No participant corrections or additional model attempts are made
after external grading.

## A: solo

Answer SHA-256:
`9834e12943c1fe738c4b07f4ea89ad5a282ecd4920c992a9d03aa66da377096f`.

All 50 decisions match the key; all 50 records have valid quotations and complete
coverage. The evaluator found no material action/scope issue in 49 records.

ISSUE-016 has an overbroad opening condition: the explanation requires catch-up
for "synchronous or failover replicas". The source's later clarification says
eligibility to become the Harbor primary is the deciding property, not transport
mode. The answer quotes that clarification, and its subsequent instructions do
refer to failover replicas, but the opening still implies a synchronous replica
is sufficient to trigger the action regardless of eligibility. It should say
failover-eligible replicas. This is a scope-fidelity concern, not a wrong
`conditional` label; the automated grader does not assess that distinction.

The answer is otherwise detailed and grounded. This review does not interpret
the automated pass as perfect factual equivalence across implementations.

Host reads of the sandbox-created answer were denied by Windows permissions.
Inspection used the existing read-only sandbox identity and an explicit Python
path, with no ACL changes, model calls or edits to the saved answer. Its hash was
stable across the inspection passes.

## C: skill-guided

Answer SHA-256:
`f86968debde70d545fb076abfa54fc86c7008efed7db5c10918db38fb47d0f8d`.

All 50 decisions match and all records have valid quotations. Every explanation
and quotation was reviewed. The same ISSUE-016 scope concern remains: C requires
catch-up for "synchronous or failover replicas" despite quoting the later
eligibility-based clarification. The other 49 records contain no material
action/scope problem found in this review. No additional substantive issue was
identified in C versus A.

The 47/50 preferred-anchor coverage diagnostic is identical in both answers and
is not a failure: source-equivalent evidence is allowed. Exact quotations prove
the words came from the source, not that the explanation reconciles them.

Both answers therefore pass the automated checks but need the same scope
wording correction for unqualified semantic acceptance. Neither answer was
edited or sent back for correction, so the recorded costs are original attempt
costs, not measured costs of corrected accepted results. This small unblinded
review cannot establish perfect equivalence or general accuracy rates.

## D: skill with required Luna Max

Answer SHA-256:
`3c8bb15923a5000a4242c07d58d4a26690946301c44cd6cf8d1b2a879152f99f`.

All 50 decisions match the frozen key; all 50 records pass the exact quotation
and coverage checks. The evaluator reviewed all final explanations and quotations
against the full source discussions, including later clarifications and scope.
No material semantic error was found. This is the same unblinded model-review
method as A/C, not a stronger claim of independently proven perfect accuracy.

ISSUE-016 correctly limits catch-up to replicas eligible to become the Harbor
primary, including asynchronous failover targets. The initial worker answer,
retained in the coordinator's command output, already had this wording. D was
not primed with A/C's error and the evaluator did not intervene during execution.

Before submission, the coordinator asked the original worker to correct three
records. ISSUE-040 had reversed the meaning of the version-stable-source restart
proposal; ISSUE-045 needed explicit supported-provider, deadline and safe
re-enrollment details; ISSUE-048 needed “configuration change” rather than the
narrower “policy change.” The final answer resolves these findings. That internal
correction pass is included in D's measured cost; no post-grading repair occurred.

The 36/50 preferred-anchor diagnostic does not indicate fourteen failed records.
The final passages provide equivalent decision support despite not reproducing
every author's preferred anchor verbatim. Additional explanation details were
checked against the underlying source, not assumed from the automated quote pass.

Inspection used the existing read-only sandbox identity, with no ACL changes or
saved-answer edits. The hash was stable across both answer inspection batches.
The [D result](results-forced-luna-2026-09-10.md) distinguishes its accepted final
artifact from A/C's cheaper original attempts that still need a scope correction.
