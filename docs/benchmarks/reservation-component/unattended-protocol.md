# Unattended execution test

Keep the existing reservation task, A/B prompts, Luna Max, B-then-A order,
objective checks and bounded Sol High correction policy unchanged. This isolates
execution/supervision rather than also introducing a larger task. Reuse the
qualified fixture; do not commission another fixture audit.

`unattended.py prepare` uses the existing repeat verification and fresh
identities. `unattended.py run` executes the frozen pair and any allowed
correction serially in host software, retaining the shared ownership guard.
After both pass it revalidates hashes, scope and added tests, then writes a
compact packet. No worker result is automatically accepted on that basis.

Launch the host as a hidden background Windows process with stdout/stderr saved
outside the worker checkouts. Confirm initial launch once, then end the live
supervising turn. Do not poll, narrate progress, add an automation or launch an
Astra/Fable reviewer worker. `STATUS.md` updates locally; there is no automatic
notification. Failed/partial runs stop according to the existing driver and
write a needs-attention report rather than creating unbounded retries.

When the user returns after completion, the original configured orchestrator
performs one substantive review across both results, reading the saved contract,
changed source, checks and handoffs. No reimplementation or redundant acceptance
test execution unless evidence has changed or a gap requires it. Inspect shared
core use and unresolved claims. Report accepted/rejected only after that review.

Account worker attempts and any corrections, plus this setup turn and the later
review turn separately and in total where telemetry is complete. The manifest
captures setup thread/turn identity to avoid attributing another user turn's
usage to launch. The comparison's fixed fixture preparation came from earlier
research and is not zero-cost; disclose its exclusion. Waiting wall-clock time
alone is not model usage. Historical API-equivalent rates are not bills or
subscription-consumption measurements.

The ignored `local-unattended.json` locates the private status, logs, original
receipts, manifests and ready-for-review packet. Preserve all earlier pairs.
