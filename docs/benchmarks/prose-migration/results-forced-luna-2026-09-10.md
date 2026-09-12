# Forced Luna control — 10 September 2026

**Luna was cheap; the complete delegated workflow was not cheaper.** Requiring
one Luna Max worker produced a final answer with no material semantic error
found in review, at **$1.6628482 API-equivalent: 27.94% above the solo attempt**.
The earlier solo and optional-delegation answers both needed one scope correction.
This is therefore not a comparison of equally accepted final results.

| Condition | Effective execution | API-equivalent cost | Automated decisions / citation records | External semantic review |
| --- | --- | ---: | --- | --- |
| A: no skill, no delegation | Astra High | $1.299660 | 50/50 / 50/50 | One scope correction needed |
| C: skill, delegation optional | Astra High; stayed solo | $1.325202 | 50/50 / 50/50 | Same scope correction needed |
| D: skill, Luna required | Astra High + one Luna Max | $1.6628482 | 50/50 / 50/50 | No material issue found after internal corrections |

D was **$0.3631882 more than A**, and **$0.3376462 (+25.48%) more than C**.
These estimates describe recorded attempts, including D's internal correction
pass. A/C were not repaired after evaluation, so their fully corrected
accepted-result costs are unknown. The review was unblinded and model-based,
not human adjudication or proof of perfect accuracy.

## What was held fixed

This control reused the [original task, corpus and checks](README.md): 50
independent synthetic Harbor migration discussions, 12,907 prose words, a cited
JSON checklist, and the unchanged deployment skill. It followed the completed
A/C pair, rather than rerunning or replacing either receipt.

The sole prompt change from C was the [41-word directive](README.md) requiring
skill use and exactly one `gpt-5.6-luna` worker at `max`, with `fork_turns="none"`.
The worker owned reading, answer writing and local checks; Astra retained final
verification. No other workers were permitted. Actual configurations and the
single child were confirmed in telemetry; no Claude worker ran.

Preflight verified identical base prompt, task tree, runtime settings, policy
hashes and grader. The original runner was untouched: a private snapshot added
one prompt-append line. The historical runner arm remains `C` internally, but
this report and the separate accounting plan identify the control as **D**.
Skill/catalogue discovery and memory suppression matched the original setup;
Astra explicitly read the supplied core skill and model-selection guide.

The run used Codex CLI 0.153.4 and the same 45-minute safety cutoff. It completed
normally in **820.51 seconds**, with no timeout, automatic trial retry, evaluator
intervention or post-grading participant edits. All frozen inputs remained
unchanged. This tests forced delegation, not spontaneous skill routing.

## Where the cost went

| Agent | Input | Cached input, included | Output, including reasoning | Responses | Largest input | Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Astra High coordinator | 543,229 | 446,208 | 2,901 | 15 | 62,642 | $1.561468 |
| Luna Max worker | 1,958,859 | 1,835,520 | 33,335 | 35 | 89,586 | $0.1013802 |
| Total | 2,502,088 | 2,281,728 | 36,236 | 50 | — | $1.6628482 |

The coordinator accounted for **93.90%** of the cost. Luna's complete attempt,
including its correction pass, cost about ten cents. Astra alone cost **20.14%
more than A's entire solo attempt**.

Astra loaded the skill, model guide and task, assigned the worker, and waited.
After the first return, it requested the full answer and all 50 source
discussions in batches, then reread ten answer records. It requested corrections
and subsequently ran structural/citation checks and inspected revised records.
Answer generation moved to Luna; the source-reading burden did not stay there.

Compared with A, Astra generated 6,652 fewer output tokens, saving $0.332600 at
the frozen rates. But it processed 50,596 more uncached input tokens and 88,448
more cached input tokens, adding $0.594408. That leaves $0.261808 more parent
cost before Luna's $0.1013802 is added. This is an arithmetic decomposition,
not a controlled estimate of the causal cost of an individual instruction.

Parent usage grouped by observed milestones was $0.569804 before the first
worker return, $0.799584 during review and the follow-up, and $0.192080 after
the correction return. These groups include all parent activity in each interval;
they are not isolated charges for spawning, waiting or reviewing.

### Waiting worked

There was one spawn, one follow-up to the same worker, and two completion waits:

| Wait | Start, UTC | Return, UTC | Result |
| --- | --- | --- | --- |
| Initial assignment | 10:27:48.368 | 10:37:56.807 | Completed; `timed_out: false` |
| Corrections | 10:39:05.606 | 10:40:17.777 | Completed; `timed_out: false` |

There was no repeated timeout-polling loop, replacement worker or interruption.
The second wait followed a real correction assignment. Waiting overhead is not
the observed failure mechanism in this trial.

## Accuracy and corrections

The external grader passed all 50 labels and all 50 citation records, plus
coverage/order, schema, date/release, length and unchanged-source checks.
Preferred-author-anchor coverage was 36/50, versus 47/50 for A/C. That diagnostic
is not an accuracy score: equivalent sufficient passages are permitted.

Before final submission, Astra requested one bounded correction pass covering:

- **ISSUE-040:** the version-stable-source proposal permits restarting imports;
  Luna's initial explanation had instead listed those sources as needing to finish.
- **ISSUE-045:** state the supported-provider requirement, deadline and safe
  re-enrollment sequence explicitly rather than leaving details only in citations.
- **ISSUE-048:** export after the final 3.x **configuration** change, not merely
  the final policy change.

The evaluator then read all 50 final explanations and quotations against the
source discussions. No material action/scope error or insufficient support for
the decisions was found. This includes **ISSUE-016**, where D correctly uses
failover eligibility rather than replication transport mode. The retained
initial answer shows that Luna already got this distinction right before
Astra's correction pass; it was not supplied by the evaluator.

See the [semantic review](semantic-review.md) for the saved-answer identity and
the limits of this assessment. The final artifact was not changed after grading.

## Takeaway

This run demonstrates a viable inexpensive worker, but **not a cost-saving
delegated workflow**. It also shows that verification was useful: the parent
caught real wording and scope problems rather than merely repeating ceremonial
checks. Removing that review would be a different workflow with unmeasured
accuracy; the ten-cent worker price is not an accepted-result price on its own.

A cheaper approach would need a demonstrably adequate verification method that
does not require Astra to reread the whole corpus. Neither a blanket prohibition
on review nor a promise that citations alone guarantee correctness follows from
these results. No operational policy was changed and no further paid trial was
launched. One synthetic sample per condition cannot establish a general model
ranking or show that delegation always costs more.

## Accounting and retained evidence

Unique own-thread response totals reconcile with each agent's cumulative usage.
Reasoning tokens are already included in output. Cache writes were zero,
service tier was unset, and no request crossed the long-context surcharge
boundary. Frozen rates per million uncached/cached/output tokens were Astra
$10/$1/$50 and Luna $0.20/$0.02/$1.20, checked against the official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages.

These are standard API-equivalent estimates, **not subscription charges or
allowance consumption**. All three participant attempts total $4.2877102.
Including the separately measured Sol fixture author gives $5.4372894,
still excluding supervisor preparation, review and evaluation overhead.

- Skill SHA-256: `32fad0645a3fdaf6f1c9973f558ccbeab195838575ca0a3b4af849456fe5646c`
- Starting task tree: `ea69aff75fedc78f6707dfbcb834e4aa4ff465f0`
- Corpus SHA-256: `9ce6813ce7c9537675567e45b6ea608374af881a0e3f89187a571cc9aef699f4`
- Final answer SHA-256: `3c8bb15923a5000a4242c07d58d4a26690946301c44cd6cf8d1b2a879152f99f`
- Astra thread: `01a08adb-682e-7911-95ab-bab29ac5441c`
- Luna thread: `01a08adb-d296-78c0-a918-584165793ea6`

The private control plan and accounting are under `forced-luna` in the original
experiment root. Its receipt basename is
`agent-deployment-prose-migration-C-gnj06z19`. Raw rollouts and answers stay local.
