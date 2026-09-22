# Assign, verify and finish

## Ownership

Start with one worker. Add workers only for independently useful scopes with settled interfaces and separate write ownership, including shared state. Name the shared state/helper owner and reuse that implementation across consumers. Keep shared integration files with one writer; queue other edits until that owner hands them back. Prefer one owner for coupled implementation, tests and corrections. Workers may redelegate only with assigned permission, supported controls and the same model restrictions.

Set model and effort explicitly, use minimal inherited history, and confirm effective settings when exposed. A full-history fork can inherit the coordinator's configuration. Report unavailable controls or mismatches rather than substituting silently. For isolated checkouts, specify the starting revision and needed uncommitted changes.

Give key entry points and enough context to start; leave local navigation to the worker:

```text
Outcome, scope and non-goals:
Owned files/resources, permissions and interfaces:
Relevant evidence, search boundaries and project instructions:
Settled decisions and rationale; choices left to the worker:
Required behavior, failure cases, shell/test command and verification owner:
Budget or observable checkpoint; report blockers promptly:
Return complete | partial | blocked, artifacts, checks/results and unresolved risks.
```

When an assignment requires repository exploration, including implementation, include:

> Context handling: Discover candidate files within the relevant paths and file types before reading bodies; exclude unrelated generated or captured content. Read matching functions or ranges. If output truncates, recover the missing relevant ranges instead of treating the partial return as complete. Widen the search when evidence or coverage requires it.

Check consequential assumptions and whether acceptance checks would detect their failure. For state-dependent behavior, supply examples or existing contract tests distinguishing status, permitted actions and side effects, including conflicting flags or missing-versus-null values where relevant. Do not leave domain meaning to inference from field names. Leave implementation choices with the owner. Diagnosis and review are read-only unless scoped reproduction or scratch edits are assigned.

For uncertain repairs, assign a runnable reproduction, discriminating test or bounded diagnostic first. Do not require proof of a presumed cause. If necessary evidence is unavailable, return the exact gap and useful artifacts instead of continuing to search. Do not add coordinator check-ins for this intermediate work.

Do not investigate an active worker's assignment in parallel or repeatedly inspect unfinished code. Review completed handoffs or agreed stable checkpoints; batch findings into one correction assignment. Intervene early for a concrete blocker, conflicting writes, an authorization issue or a user change, not to provide piecemeal suggestions. Handoffs preserve partial edits/tests, exact commands/results and unresolved questions. Absence claims need search scope; completeness claims need coverage or count reconciliation. Report actual truncation, not merely a configured limit.

## Verification

Choose one substantive verification owner before dispatch. Separate objective checks from judgments: schema, exact quotations and test execution do not establish supported claims or correct behavior outside the checks. Reuse an existing contract-derived checker where suitable. Worker-written tests can supplement it; independently assess that the checks enforce the requirement. Do not add arbitrary formatting restrictions or weaken assertions to fit a result.

Have the writer run objective checks before returning the artifact. Use concise results tied to the checked revision; retain complete logs for failures. The coordinator can rerun a trusted checker without reimplementing it or loading its full output into model context. Do not generate a second answer to compare when a direct check suffices.

Delegate substantive review only when its coverage or independence justifies the cost and there is a basis for trusting it on the relevant error types. Price, full file coverage and a confident approval do not establish that competence. Without adequate verification evidence, retain direct review of the unresolved requirements. Do not add a standing reviewer or automatically raise its effort.

The verification owner compares the artifact with the original sources or contract, including material scope, chronology, affected interactions and counterexamples. Resolve worker-flagged judgment calls against the source before accepting affected claims; relaying them is not verification. Prioritize meaning and behavior errors over optional hardening. Distinguish material defects, missing details and wording preferences; report ambiguity in the source or requirement rather than treating a disputed interpretation as certain.

Return the checked artifact/revision, coverage and gaps, objective check results, and findings with location, trigger, impact and evidence. Route corrections using the recovery rules below; recheck changed risks and affected interactions, reusing valid evidence for unchanged work.

The coordinator retains final acceptance. Start with the diff, executable results and consequential judgment calls; do not routinely retrace the worker's investigation or repeat a qualified review. Read supporting source for gaps, contradictions or insufficient evidence. If full source review is necessary, account for it before dispatch. Sampling cannot replace required full coverage.

Finish when required checks and inspection support acceptance. Do not expand optional hardening or housekeeping. Only the coordinator may revise acceptance criteria within user authority. Process success, passing self-checks and a review's completion status are not acceptance.

## Recovery

After confirmed termination, a verified mechanical fix permits a safe rerun within existing scope and budget without renewed permission. Preserve failure evidence and announce the retry. Reassess repeated failures; ask before material extra spending or actions outside existing authority. Never retry with uncertain ownership or duplicate side effects.

Return bounded defects within a sound approach to the worker with the failing case and expected behavior. Separate provider/runtime errors and changed requirements from implementation failures. For changed requirements, update the example and recheck affected behavior. After ownership is released, handle a tiny integration fix locally if another handoff costs more.

- **Blocked:** Resolve missing decisions, evidence or access within authority; changing models is not the default fix.
- **Partial:** Preserve usable progress. If no usable artifact resulted, redispatch only when narrower scope, new evidence or a verified runtime fix addresses the failure; otherwise finish locally or report the blocker. A longer briefing or larger budget alone is insufficient.
- **Substantive failure:** The core approach fails the required behavior, or newly exposed design work exceeds the assignment. Return the decision to the orchestrator.

Reassess the contract and approach after substantive failure; do not follow an automatic model ladder. Finding defects is successful review.

Reuse suitable owners. Before transferring writes, confirm the previous worker and its writing commands stopped; pass the diff, failures and open questions. If termination is uncertain, keep successors read-only or non-overlapping. Preserve unrelated edits.

## Waiting and accounting

For detached CLI work, use [waiting.md](waiting.md) to queue one follow-up after the process exits and its receipt is saved. Confirm the target task, retain delivery status and end the turn when independent work is exhausted. Do not prequeue status checks: queued input alone is not proof that a worker finished.

Before dispatch likely to leave the coordinator idle, identify a supported completion notification or wait within host responsiveness rules. Otherwise confirm the job can safely survive the turn ending and explain that the user must check back. If neither is possible, stay local or report the limitation before dispatch. Reuse this finding until the runtime changes; timeout configuration alone does not prove availability.

Use completion notifications or event-driven waits with supported cursors. Prefer the configured wait default when permitted by higher-priority responsiveness rules and tool limits; shorten it only for a deadline or meaningful checkpoint. Do not replace completion waits with repeated sleeps, status polls, wrapper polling or automations, or wake merely to preserve a cache. If blocking-wait limits conflict with the tool, use a supported host-managed completion route or report the limitation; do not override the limit through assignment wording.

If no supported completion mechanism is available and independent useful work is exhausted, leave only safely persistent work running. State what is running, where results will be saved, what remains pending and a rough remaining-time range from existing evidence (or unknown). Say: "I'm stopping polling. Please check back with me to inspect the result and continue; I won't automatically resume." End the turn; do not create an automation unless requested. On return, inspect once: verify and continue if complete; otherwise report briefly and stop again.

An empty timeout proves neither failure nor health. Use the supported completion route or the fallback above; do not add reads, restart, replace or duplicate work merely because a wait ended. At a due checkpoint use one compact non-interrupting check. Preserve safety timeouts: a wait timeout differs from a work timeout that terminates the worker.

When measuring, retain session IDs and assignment/review boundaries; recover usage from existing traces after completion, not periodic accounting calls. A missing handoff receipt does not establish missing telemetry. Count parent and child input/cache use, output, preparation, review, failed attempts and integration. Keep unrelated parent work separate from delegation overhead and attempt cost separate from cost through acceptance. API estimates are not subscription allowance; cache-write share alone is not net cache cost.
