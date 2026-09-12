# Assign, verify and finish

## Ownership

Start with one worker. Add workers only for independently useful scopes with settled interfaces and separate write ownership, including shared state. Keep shared integration files with one writer; queue other edits until that owner hands them back. Prefer one owner for coupled implementation, tests and corrections. Workers may redelegate only with assigned permission, supported controls and the same model restrictions.

Set model and effort explicitly, use minimal inherited history, and confirm effective settings when exposed. A full-history fork can inherit the coordinator's configuration. Report unavailable controls or mismatches rather than substituting silently. For isolated checkouts, specify the starting revision and needed uncommitted changes.

Give a short, self-contained assignment:

```text
Outcome, scope and non-goals:
Owned files/resources, permissions and interfaces:
Relevant evidence, search boundaries and project instructions:
Settled decisions and rationale; choices left to the worker:
Required behavior, failure cases, checks and verification owner:
Budget or observable checkpoint; report blockers promptly:
Return complete | partial | blocked, artifacts, checks/results and unresolved risks.
```

When an assignment requires repository exploration, including implementation, include:

> Context handling: Discover candidate files within the relevant paths and file types before reading bodies; exclude unrelated generated or captured content. Read matching functions or ranges. If output truncates, recover the missing relevant ranges instead of treating the partial return as complete. Widen the search when evidence or coverage requires it.

Challenge consequential assumptions and whether the checks would detect their failure before dispatch. Leave local implementation choices with the owner. Following known test patterns with settled expectations can be mechanical; discovering unfamiliar failure cases is reasoning work. Diagnosis and review are read-only unless scoped reproduction or scratch edits are assigned.

Do not investigate or implement an active worker's assignment in parallel. Work on independent responsibilities or wait. Handoffs link artifacts and preserve exact failures, constraints and decision-critical evidence. Absence claims need search scope; completeness claims need coverage or count reconciliation.

## Verification

Choose one substantive verification owner before dispatch. Separate objective checks from judgments: schema, exact quotations and test execution do not establish supported claims or correct behavior outside the checks. Reuse an existing contract-derived checker where suitable. Worker-written tests can supplement it; independently assess that the checks enforce the requirement. Do not add arbitrary formatting restrictions or weaken assertions to fit a result.

Have the writer run objective checks before returning the artifact. Use concise results tied to the checked revision; retain complete logs for failures. The coordinator can rerun a trusted checker without reimplementing it or loading its full output into model context. Do not generate a second answer to compare when a direct check suffices.

Delegate substantive review only when its coverage or independence justifies the cost and there is a basis for trusting it on the relevant error types. Price, full file coverage and a confident approval do not establish that competence. Without adequate verification evidence, retain direct review of the unresolved requirements. Do not add a standing reviewer or automatically raise its effort.

The verification owner compares the artifact with the original sources or contract, including material scope, chronology, affected interactions and counterexamples. Resolve worker-flagged judgment calls against the source before accepting affected claims; relaying them is not verification. Prioritize meaning and behavior errors over optional hardening. Distinguish material defects, missing details and wording preferences; report ambiguity in the source or requirement rather than treating a disputed interpretation as certain.

Return the checked artifact/revision, coverage and gaps, objective check results, and findings with location, trigger, impact and evidence. Route corrections using the recovery rules below; recheck changed risks and affected interactions, reusing valid evidence for unchanged work.

The coordinator retains final acceptance. Inspect that evidence and unresolved findings without routinely repeating a qualified delegated review. Read underlying sources for gaps, contradictions, consequential disputed decisions or insufficient evidence. If full source review is necessary, account for it before dispatch; it is neither free nor automatically a reason to reject all delegation. Sampling cannot replace required full coverage.

Finish when required checks and inspection support acceptance. Do not expand optional hardening or housekeeping. Only the coordinator may revise acceptance criteria within user authority. Process success, passing self-checks and a review's completion status are not acceptance.

## Recovery

Return mechanical errors and bounded defects within a sound approach to the worker, with the failing case and expected behavior. The coordinator may handle a tiny integration fix when another handoff would cost more, after ownership is released. Local tool errors and expected failing regression tests are not assignment failure. Do not repeat an approach without new evidence.

- **Blocked:** Resolve missing decisions, evidence or access within authority; changing models is not the default fix.
- **Partial:** A checkpoint, turn limit or budget ended. Preserve progress; continue only with a credible plan within user limits.
- **Substantive failure:** The core approach fails the required behavior, or newly exposed design work exceeds the assignment. Return the decision to the orchestrator.

After one substantive non-trivial Luna failure, do not repeat the assignment on Luna. Choose local completion or a revised bounded assignment to another allowed worker, not an automatic escalation ladder. Finding defects is successful review.

Reuse suitable owners. Before transferring writes, confirm the previous worker and its writing commands stopped; pass the diff, failures and open questions. If termination is uncertain, keep successors read-only or non-overlapping. Preserve unrelated edits.

## Waiting and accounting

Before dispatch likely to leave the coordinator idle, confirm a supported completion wait within host responsiveness rules. Reuse that finding until the runtime changes. If unavailable, stay local or report the limitation; timeout configuration alone does not prove availability.

Use completion notifications or event-driven waits with supported cursors. Prefer the configured wait default when permitted by higher-priority responsiveness rules and tool limits; shorten it only for a deadline or meaningful checkpoint. Do not replace completion waits with repeated sleeps, status polls, wrapper polling or automations, or wake merely to preserve a cache. If blocking-wait limits conflict with the tool, use a supported host-managed completion route or report the limitation; do not override the limit through assignment wording.

An empty timeout proves neither failure nor health. Continue waiting without extra reads or replacement unless a due checkpoint, blocker or exhausted budget requires action. At a checkpoint use one compact non-interrupting check. A wait timeout differs from a work timeout that terminates the worker.

When measuring, retain session IDs and assignment/review boundaries; recover usage from existing traces after completion, not periodic accounting calls. A missing handoff receipt does not establish missing telemetry. Count parent and child input/cache use, output, preparation, review, failed attempts and integration. Keep unrelated parent work separate from delegation overhead and attempt cost separate from cost through acceptance. API estimates are not subscription allowance; cache-write share alone is not net cache cost.
