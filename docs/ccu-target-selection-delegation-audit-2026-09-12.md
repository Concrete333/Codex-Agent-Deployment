# CCU target-selection delegation audit

Run dated 12 September 2026; audit completed 13 September. Read-only audit of the real Spaceships catalogue implementation; no new model trial, application edit, live action or full-suite rerun.

## Findings

The bounded worker completed useful production implementation, including its corrections. The evidence does not support replacing Luna, adding a reviewer or claiming a saving. The clearest avoidable work was overly broad exploration and integration across files being changed by both owners.

This corrects an implication in our initial interpretation: the coordinator's report said it integrated changes “including fixes,” but that does **not** mean Astra wrote those fixes. The worker's recorded patches show Luna implementing the outside-folder, ambiguity, serialization, authority, stale-signature and UI-disclosure corrections before its final handoff. The worker explicitly attributes the final UI-disclosure request to parent review. Discovery credit for every earlier issue is not established from the inspected evidence.

### Correction classification

| Observed change in Luna's patch history | Assessment |
|---|---|
| Stop seeding selected targets from registered assets outside the enumerated folder; report one path registered to multiple ships as ambiguous | Material implementation defects relative to exact folder scope. Local repairs within the existing approach, not evidence the whole design failed. |
| Serialize `Path` objects as strings in the mapping signature | Mechanical boundary defect. Suitable for correction by the existing worker. |
| Reject nonempty requested IDs when ship authority is unavailable | Validation correction. Initial code deliberately tolerated a missing table for minimal fixtures; tests must not define weaker production authority. |
| Reject a stale supplied folder signature; preserve explicit invalid values rather than replacing them through truthiness | Required review/save consistency. A bounded behavioral repair, not optional hardening. |
| Freeze saved UI scope into a new batch when the request omits it, including the default `prepare` action | Integration gap between displayed scope and action scope. The worker identified this remaining path in commentary and repaired it. |
| Show filename, ship label and ID rather than only a count | Parent-requested acceptance/UI disclosure refinement. The broad reviewability requirement existed; exact presentation was not independently established as frozen before dispatch. |
| Handle minimal legacy fixtures and frozen recovery selections | Compatibility/integration work, not automatically a failed worker assignment. One patch disabled current known-ID validation for replay of a previously validated frozen scope. Its stated contract rationale must be assessed separately from making a fixture pass; this audit is not a fresh correctness certification of that behavior. |

These fixes retained the shared scope module and its interfaces. Returning bounded corrections to Luna was appropriate; failed core behavior or newly exposed architecture would require the orchestrator to reassess instead.

## Ownership was less isolated than the task label suggested

The parent and worker both changed `ccu_listing_launch.py`, `sales_opportunities.py` and `ccu_listing_queue.py` during the worker's active interval. The parent was implementing recovery, catalogue expansion and route eligibility; Luna was integrating destination filtering into the same modules. Those are distinguishable responsibilities, but they have shared interfaces and test fixtures.

Parent patch ordinals 659, 753, 887, 895 and 1004 show those integration changes. In particular, ordinal 895 changes how the queue calls scoped catalogue discovery. The worker then had to reason about the combined working tree, not a frozen independent component. There were 11 parent `send_message` calls to the worker and one 25-minute completion wait. Messages are not all polling or waste; their complete semantic contents were not available in the bounded parent thread view, so this audit does not classify every message.

The worker's test trace records both legacy-schema errors and failures in the parent's newly added recovery tests. It repaired its side of those interactions. This supports an integration-cost mechanism, not proof of a lost update or a specific dollar amount wasted. Shared file reads alone do not prove duplicate implementation.

For similar work, identify the shared entry points before dispatch. Give one writer those integration files, or serialize the edits and hand ownership back explicitly. The parent can continue independent recovery research or other non-overlapping work. Do not split implementation and tests into additional agents.

## Exploration produced unnecessary context

The worker made 116 command calls, seven with nonzero exit codes, and underwent one recorded context compaction. Not all failures were wasted work: some were legitimate failing regression tests. Shell mistakes also included a nonexistent test filename, PowerShell range syntax, a Bash heredoc in PowerShell and unsupported shell-style globs passed to `rg`.

One search for `DEPENDENCIES|GET|do_GET|do_POST|api_assumptions` included the entire `tests` tree and captured HTML fixtures. The saved command output has **1,048,606 original characters**, despite piping to the first 100 lines: minified HTML can occupy one enormous line. This is an output-size observation, not one million billed tokens. Retrieval truncation is also not proof that every character entered the worker's model context.

A no-model diagnostic during this audit applied the same query only to `test_*.py` files under `tests`: **27 matching lines, 2,362 characters**, exit zero. That demonstrates how file-type scoping avoids the captured HTML; it is not a matched model trial, proof of exhaustive semantic coverage or a measured API saving. Discover actual filenames first rather than guessing `test_navigator_http.py`.

The existing search paragraph was conditional on “repository-search assignments.” An implementation worker also explores a repository. Its trigger now covers that case, without adding a second search procedure or a catalogue-specific rule.

## Accounting recovered from local traces

| Completed scope | Responses | Input, including cache | Cached input | Output, including reasoning | Historical API equivalent |
|---|---:|---:|---:|---:|---:|
| Astra Light implementation turn | 121 | 17,059,588 | 16,848,768 | 45,158 | $21.214868 |
| Luna Max assignment | 143 | 17,301,160 | 16,887,040 | 64,443 | $0.4978964 |
| Combined | | | | | **$21.7127644** |

Per-response records were deduplicated by response ID within each thread/turn; sums reconcile to completed-turn counters. Effective configurations were Astra `low` (Light) and Luna `max`. Rates are the retained experimental rates, not current pricing: Astra $10/$1/$50 and Luna $0.20/$0.02/$1.20 per million uncached-input/cached-input/output tokens. No cache-write tokens were recorded for these completed scopes. Cached input and reasoning output are not charged twice.

The parent turn includes recovery, catalogue routes, submission-journal development, live-state inspection, integration and final reporting. It is **not** the cost of accepting Luna. Earlier planning, subsequent turns and this audit are excluded. We cannot separate target-selection review from mixed parent responses reliably enough to quote a precise acceptance price. There is no solo comparator and no subscription-allowance inference.

The final logs show 51 focused tests passing and 2,567 full-suite tests run successfully with one skipped. Passing suites do not independently prove all scope/safety requirements. Nothing in this audit changes the launch guard or turns individual draft readiness into publication authority.

## Skill changes and next observation

The repository and installed delegation guide now:

- return mechanical and bounded defects within a sound approach to the worker; return failed core approaches and newly exposed design decisions to the orchestrator;
- allow a tiny local integration repair when another handoff would cost more, after ownership is released;
- keep shared integration files with one writer;
- apply existing exploration guidance to implementation assignments too;
- retain session IDs and phase boundaries for after-the-fact accounting, separating unrelated parent work from delegation overhead.

The README's correction description is aligned. No model, effort, acceptance standard or worker allowance changed. These are operational clarifications and a narrow scope correction, not measured savings claims.

Do not spend on another synthetic run merely to validate these sentences. On the next authorized real assignment, observe whether the worker avoids generated/captured context, has stable shared interfaces, and returns bounded corrections without a competing parent implementation. Use existing traces rather than periodic accounting. Keep review unchanged until a separate consequential-defect/clean-control experiment establishes that a cheaper or smaller review preserves required accuracy.

## Evidence locators

- Project record: `C:\Users\cwbec\Spaceships\plans\ccu-catalogue-launch-2026-09-12.md`; ignored `ccu-launch-session-2026-09-12.local.json` beside it.
- Parent thread: `01a09781-921e-79a3-8497-b97ecaafcefa`; measured turn: `01a097a8-f1a9-77c3-9606-cc72ff4e2f59`.
- Worker thread: `01a097a9-c602-7e50-9115-a2777f4fc65a`; turn: `01a097a9-c6a6-7103-8302-978dfc7cb44a`; task: `/root/l1_target_selection`.
- Native rollouts: `C:\Users\cwbec\.codex\sessions\2026\09\12\rollout-2026-09-12T22-24-06-01a09781-921e-79a3-8497-b97ecaafcefa.jsonl` and `rollout-2026-09-12T23-08-01-01a097a9-c602-7e50-9115-a2777f4fc65a.jsonl` in that directory. Later parent activity must be excluded by turn ID.
- Worker patch IDs: `exec-28ba8c53-4bc2-4219-a4c6-d25b3b3e7ddd` (folder/ambiguity/serialization), `exec-1ca6d733-718a-429e-bbf2-e2ec7df48c28` (authority), `exec-f5242c68-327a-415e-8db6-12a5f053db3d` (stale save), `exec-ae0da969-eb5b-4361-bccb-a7c3a638bab7` (disclosure).
- Large search: worker command `exec-6c743034-4305-435b-bdaa-1fc8ee7f8b82`. Its unbounded source output is retained by the original task; do not load it merely to recount its size.

The audit used saved command/patch evidence, not a new paid reviewer or live reproduction. Parent task retrieval omitted the target turn's item bodies; native tool-call inputs and counters were used where available. Claims about the exact original assignment wording, attribution of every discovery and per-finding parent cost remain unverified.
