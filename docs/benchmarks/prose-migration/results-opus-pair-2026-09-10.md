# Opus 5 Low builder and reviewer — 10 September 2026

**Neither test met the acceptance standard.** The builder classified every record
correctly but failed exact-quotation checks on five records. The independent
reviewer returned no findings on Luna's initial answer, missing the three issues
previously identified by Astra.

Those three comparison concerns are not equally severe. A subsequent source
audit found conflicting source/reference wording for ISSUE-048; see the
[Sol report's clarification](results-sol-review-2026-09-10.md). ISSUE-045 is a
completeness concern. Missing ISSUE-040's meaning reversal remains clear evidence
against treating either reviewer as a qualified substitute on this sample.

| Test | Captured API-equivalent cost | Result |
| --- | ---: | --- |
| Opus owns writing, self-checks and corrections | $1.02065325 | 50/50 decisions; 45/50 valid citation records; not accepted |
| Opus reviews the saved initial Luna answer | $0.58429925 | No findings; all three comparison issues missed |
| Total for these two sessions | $1.60495250 | No retry or post-evaluation repair |

These are worker-only costs, including provider-reported helper usage, not the
cost of a complete Astra-led workflow or subscription allowance measurements.

## Builder: correct categories, an inadequate self-check

The builder received the original task and 50 discussions, with no starter
answer, gold labels or earlier findings. It wrote `answer.json` and a local
`check.py`, and reported that all its checks passed.

The unchanged external grader returned:

- All 50 classifications correct, all IDs present and ordered.
- Five invalid citation records: ISSUE-002, ISSUE-016, ISSUE-017, ISSUE-038 and
  ISSUE-044. The others passed exact-quotation and line/length checks.
- Original task and source files unchanged.

The five records contain inserted `...` omissions. The contract permitted
whitespace normalization, not changes to quoted text. The worker's checker split
quotes on `...` and checked that the remaining fragments occurred in order.
That is a weaker rule than exact matching, so its success did not establish
acceptance. Its completion message explicitly described the ellipsis exception;
there is no need to infer deceptive intent.

All 50 saved explanations and their quotations were inspected against the
previously reviewed source material, with focused source checks for concerns.
The answer correctly handles the replica-eligibility distinction in ISSUE-016
and the configuration-change boundary in ISSUE-048. Its ISSUE-045 explanation
includes the supported-provider requirement and deadline that Luna omitted.

An additional wording concern remains in ISSUE-015: “that opt-in must happen
before the next event is sent” attaches the deadline to opting in, whereas the
source requires the **receiver to accept v4** before the next event. The answer
cites the correct source sentence, but the explanation should preserve its
subject and timing. This is separate from the five mechanically invalid quotes.
The review is unblinded and model-based, not human adjudication or a comprehensive
estimate of error rates.

The builder's $1.02 is therefore an unaccepted original-attempt cost. It cannot
be presented as an accuracy-preserving saving over the $1.30 solo Astra attempt,
which also required a different semantic correction.

## Reviewer: read all sources but missed the defects

The reviewer ran in a different checkout and fresh session. It received exactly
the initial Luna answer used in the Sol review, not Opus's new answer. It was not
told any defect existed, given a finding count, or shown prior results.

| Comparison issue in Luna's initial answer | Sol High | Opus 5 Low |
| --- | --- | --- |
| ISSUE-040: restart permission described as a requirement to finish | Missed | Missed |
| ISSUE-045: explanation omits procedure/deadline detail | Missed | Missed |
| ISSUE-048: final configuration change narrowed to final policy change | Found | Missed |
| Review-only cost | $0.5635768 | $0.58429925 |

ISSUE-045 is an explanation-completeness concern, and some details already
appear in its citation. Even setting aside that concern and the disputed
ISSUE-048 wording leaves ISSUE-040's substantive meaning reversal missed by
Opus. The three findings are comparison cases,
not an exhaustive independently adjudicated gold set.

The saved Claude trace confirms Read calls for all 50 discussions, TASK.md and
the answer. Its final report claimed full coverage and returned an empty findings
list. There are no proposed corrections to label false positives, but silence
is not evidence of a reliable reviewer. No correctness hints or follow-ups were
sent, and no result was repaired after evaluation.

The reviewer had Read/Glob/Grep tools only, unlike Sol's shell-enabled read-only
session. It correctly disclosed that it could not run parsing, hashing or word
count checks. The harness supplied the input hash, and the external grader had
already verified the candidate's structure and quotation validity. The missed
problems require semantic comparison, but the tool and prompt differences still
prevent a strict model-only causal conclusion.

## Controls, execution and cost

The [runner](opus_pair.py) made one sequential batch through the existing Claude
wrapper, with two separate checkouts and sessions. Each requested
`claude-opus-5` at `low`, a 2,700-second cutoff and a $5 API-equivalent safety cap.
The builder had edit and local-shell tools; the reviewer had read-only tools.
There was no third agent, billable rerun or test-time policy change.

Claude Code 2.1.266 was authenticated through the existing first-party Claude.ai
subscription. Inherited global instructions were inspected. Skill discovery,
settings sources and configured MCP servers were disabled by the wrapper;
Claude's default coding prompt remained. The checkouts were newly created, with
no prior project memory. This wrapper is not an operating-system sandbox.

Both sessions returned normally, with no permission denials, reported errors,
stderr or timeouts. The builder took 194.07 seconds and the reviewer 68.67.
All frozen input files, request and wrapper identities remained unchanged.
The main assistant messages in both traces identify `claude-opus-5`; requested
Low effort is recorded in the command, but not independently verified by the
wrapper's receipt. Five-minute cache writes were confirmed for both sessions.

| Main Opus usage bucket | Builder | Reviewer |
| --- | ---: | ---: |
| Uncached input | 18 | 98 |
| Cache creation input | 65,111 | 62,205 |
| Cache read input | 250,045 | 41,430 |
| Output, including thinking | 19,499 | 6,921 |
| Thinking, already included above | 851 | 245 |

These Claude input buckets are separate, unlike the inclusive input counters in
the Codex reports. The provider's main-model costs were $1.01953125 and
$0.58301125. Receipts additionally included `claude-haiku-4-5-20251001` usage of
$0.001122 and $0.001288 respectively. Both are included in the displayed totals;
the presence of internal helper usage is not evidence that the assigned worker
fell back from Opus. The saved assistant traces show Opus for the task work.

Totals are provider-reported list-price equivalents and reconcile with the sum
of reported per-model costs. They exclude supervisor preparation, external
grading and semantic review, and any future coordinator acceptance or repairs.
Neither the API-equivalent safety cap nor these receipts measure remaining
subscription allowance or enforce account-side paid-overflow settings.

## Takeaway

Moving the whole deliverable to Opus Low did not eliminate errors or make its
self-authored checker authoritative. Moving Luna's review to Opus Low did not
recover the missing semantic coverage. These observations do not establish that
Opus is generally worse than Luna, Sol or Astra; they do reject assuming either
workflow is an adequate replacement on this sample.

A fixed contract-derived checker could have exposed the builder's quotation
mistakes cheaply before submission. That is a concrete next mechanism to test,
not proof that semantic verification can be removed. No operational skill
changes or further paid tests followed these results.

## Retained identities

- Builder session: `4e1da30e-5394-46a0-b4d1-7bd6dc97327a`
- Reviewer session: `193d8610-11e6-45a4-a27d-480518a0381f`
- Builder answer SHA-256: `13aa4fbc5a1abe584847a3a5f9f522af9b4300b980ce8f7b019ed97c72f2a9b6`
- Review input SHA-256: `8842b97ada5925862d1b88d5c934199286e3c237168c0096edd8560697610d1f`
- Private receipt directory: `opus-pair/claude-worker-receipts-3dakee9h` under the
  original prose experiment root.

Private manifests retain input, request, wrapper and script hashes. Full
provider receipts, task artifacts and session traces stay local.
