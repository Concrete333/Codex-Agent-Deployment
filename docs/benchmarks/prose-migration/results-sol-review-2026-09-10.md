# Sol High review-only diagnostic — 10 September 2026

**Sol's review cost $0.5635768 API-equivalent and reported one of the three
concerns Astra previously corrected.** That finding has a reference-wording
ambiguity described below. The missed issues include an actual
reversal of a proposal's meaning. This run does not establish an
accuracy-preserving replacement for Astra's substantive review.

## Result

| Previously identified issue | Sol result | Evaluator assessment |
| --- | --- | --- |
| ISSUE-040: restart permission described as a requirement to finish | Missed | Material explanation error remains |
| ISSUE-045: recovery-key procedure and deadline insufficiently explicit | Missed | Action-detail omission remains; some details are present in the answer's citation |
| ISSUE-048: final configuration change narrowed to final policy change | Reported | Source/reference wording conflict; disputed severity |

Sol returned one finding whose proposed correction matches the authoritative
source's wording. A later audit found that the author's own reference rationale
uses the candidate's wording; the finding is not an uncontested accuracy point.
It reported all 50 IDs reviewed, no coverage gaps, and successful structural and
citation checks. Its `complete` status means the review finished, not that the
candidate answer was correct. No writer repair or follow-up review was run.

The evaluation distinguishes severity: ISSUE-045 is an explanation-completeness
concern, not a false category or invented fact. Even if that omission is treated
as non-blocking, Sol still missed ISSUE-040's incorrect account of the competing
proposals. The source permits restarting version-stable imports; the answer
describes finishing them. Correctly labeling the decision `unresolved` does not
make that explanation faithful.

The three comparison findings are not an exhaustive independently adjudicated
gold set. The evaluator accepted additional findings in principle and checked
Sol's actual finding against the source; this was not an exact-string match test.
One review cannot establish general recall, precision or model superiority.

The later audit confirmed that ISSUE-048's author rationale says “policy change”
while its decisive passage says “configuration change”; another source paragraph
also discusses preventing later policy edits. This is a fixture ambiguity to
adjudicate before using that case as a qualification gate, not proof either
wording is harmless. ISSUE-045 remains a completeness concern. Both reviewers'
miss of ISSUE-040 is the clearest retained failure evidence. No frozen fixture,
candidate, finding or numerical usage receipt was changed by this clarification.

## Inputs and isolation

The 163-word assignment requested a read-only substantive review against the
original task and all 50 discussions, including decisions, actions, scope,
uncertainty, authority and chronology. It requested material evidence-backed
findings without suggesting any defect existed or specifying a finding count.

The candidate was Luna's **initial** answer from the
[forced-worker trial](results-forced-luna-2026-09-10.md), recovered from the
coordinator's retained first-answer command output (`item_7`). Parsed content was
preserved; JSON formatting was normalized and hashed separately. The corrected
final answer was not used. Original task and source bytes match the frozen
corpus. The external structural grader also passes this initial candidate:
50/50 classifications and 50/50 valid citation records. This demonstrates why
the substantive review matters.

Only the original task, candidate answer and source discussions were placed in
the reviewer checkout. Known defects, answer keys, prior findings, research,
personal memory and routing documents were not supplied. The skill informed the
supervisor's reviewer assignment; the reviewer did not load the skill itself.
This is a worker-capability diagnostic, not a new full skill/no-skill comparison.

The runner reused the original A isolation settings with the model changed to
`gpt-5.6-sol`, effort retained at `high`, and sandbox changed to read-only.
Delegation and web search were disabled. Discovery and file-read preflights ran
before inference. An offline preflight encountered a Windows text-decoding error;
explicit UTF-8 fixed it before the single paid run. No global settings or ACLs
were changed.

## Execution and accounting

| Measurement | Value |
| --- | ---: |
| Effective configuration | GPT-5.6 Sol / High |
| Input tokens | 491,648 |
| Cached input, included | 437,632 |
| Output tokens, including reasoning | 8,623 |
| Reasoning output, included above | 5,120 |
| Responses | 14 |
| Largest response input | 52,012 |
| Captured API-equivalent cost | $0.5635768 |
| Runtime | 315.88 seconds |

The process completed normally, without timeout, nested workers, intervention or
model retry. All input hashes remained unchanged. The trace contains commands
reading all 50 discussions, additional rereads and structural checks. No
truncation marker was found in the saved command outputs. One PowerShell quoting
failure was corrected locally and is included in the measured usage.

Sol's reported answer hash, ordered coverage IDs and finding quotation were
checked independently. Reading every file and reporting full coverage did not
prevent semantic misses.

Unique own-thread response usage reconciles with the final cumulative counters.
Cache writes were zero and the service tier was unset. Frozen standard token
rates were $4/M uncached input, $0.40/M cached input and $20/M output, consistent
with the checked [official Sol page](https://developers.openai.com/api/docs/models/gpt-5.6-sol).
Reasoning is not charged a second time in this calculation.

This price covers **the Sol review only**. It excludes preparation, supervisor
dispatch and evaluation, writer execution, repairs and subsequent acceptance.
It is an API-equivalent estimate, not a subscription charge or allowance reading.
It cannot be compared with the previous $1.66 whole workflow as an end-to-end
saving. Astra's earlier review cost groups also include coordination/correction
activity, so they are not a clean matched reviewer-only baseline.

## Implication

Do not yet treat Sol High as an interchangeable replacement for Astra on this
review task. The cheaper-review proposal reduced the price of the reviewing
model, but has not demonstrated retained accuracy. Ownership changes still need
an adequate checker; a confident coverage report alone is insufficient.

No operational skill changes, hints to the reviewer, automatic effort escalation
or additional paid tests followed this result. The original candidate and review
remain unchanged for subsequent authorized comparisons.

## Retained identities

- Reviewer thread: `01a08b00-cd8c-78e3-9cf2-0bf383f7a2bd`
- Input answer SHA-256: `8842b97ada5925862d1b88d5c934199286e3c237168c0096edd8560697610d1f`
- Private receipts: `sol-review` under the original prose experiment root
- Public runner: [review_only.py](review_only.py)

The private manifest contains the command, runtime settings, source hashes,
prompt hash, initial-answer provenance and script hash. Result, full review,
events and reconciled accounting stay local.
