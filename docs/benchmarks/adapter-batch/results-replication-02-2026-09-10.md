# Frozen replication — 10 September 2026

The required-Luna workflow was cheaper again: **10.4%** in this repeat, compared
with 18.4% in the [first pair](results-2026-09-10.md). Both repeat submissions
passed all 226 frozen external cases and two additional large-CSV probes.
The additional probes exposed a gap in the original reference and both first-pair
submissions, so the frozen pass count must not be read as full conformance.

## Results

| Pair | Astra High solo | Astra High + one Luna Max | Team saving | Frozen cases, each submission |
| --- | ---: | ---: | ---: | --- |
| First | $1.099710 | $0.89779328 | 18.4% | 226/226 |
| Repeat | $1.383602 | $1.23928416 | 10.4% | 226/226 |
| Combined spending | $2.483312 | $2.13707744 | 13.9% | All four passed |

These are API-equivalent participant costs, including review and corrections,
not subscription charges or allowance measurements. Shared benchmark preparation,
supervision and external evaluation are excluded as in the first pair. Combined
spending is a descriptive aggregate over two runs per condition, not a statistical
estimate of general savings.

The repeat solo run finished in 342.67 seconds, the team in 959.63 seconds. Neither
timed out or received evaluator-fed repairs. Solo added 15 passing test methods;
the team added six. Their coverage differs, so method counts are not accuracy scores.

## Actual configuration and cost

| Repeat participant | Input including cached | Cached input | Output including reasoning | Cost |
| --- | ---: | ---: | ---: | ---: |
| Solo Astra High | 296,654 | 226,432 | 9,099 | $1.383602 |
| Team Astra High | 364,416 | 297,472 | 3,191 | $1.126462 |
| Luna Max, including corrections | 2,242,732 | 2,115,328 | 37,529 | $0.11282216 |

Own-thread usage reconciles for all three participants: 11, 15 and 45 model
responses respectively. Reasoning is included in output; there are no cache-write
tokens or large-input pricing adjustments. Rates and accounting are unchanged
from the first report. The team used **8.79 times as many input tokens** as solo.
Its coordinator accounted for 90.9% of spending.

The coordinator used more input than solo but generated 5,908 fewer output tokens.
That reduced Astra output spending by $0.295400, while its input/cache spending
increased by $0.038260. Subtracting the worker's $0.11282216 leaves the measured
$0.14431784 saving. This breakdown is accounting, not a causal ablation of skill rules.

Cache variation matters: solo's cached-input share fell from 89.3% in the first
pair to 76.3% in the repeat. The team coordinator's share also fell, from 89.3% to
81.6%. Cache state was not controlled. Do not explain the different bills solely
through model behavior or assume the observed percentage will recur.

Telemetry confirms exactly one `gpt-5.6-luna` child at `max`, with
`fork_turns="none"`; the coordinator remained `gpt-6-astra` at `high`.
No nested workers, model switches, replacement workers or Claude calls occurred.
There were two long native waits, for initial work and a correction round, with
no short polling loop. The writer retained implementation and correction ownership.

## Review caught a real defect again

The worker returned a version passing the 140 visible cases and its five initial
regression methods. Astra reviewed the implementation and independently found
Python's default CSV field-size limit: it rejected a valid memo longer than
131,072 characters, although the contract sets no such limit.

The coordinator returned this to Luna. Luna replaced the limited CSV reader with
local parsing and added long-field coverage. Astra rechecked the changed code,
reran the checks, and verified **1,200 generated CSV writer round trips**. Those
coordinator-generated checks are included in the workflow cost; they are separate
from the 226 external cases. Final external grading also confirmed protected-file
integrity and allowed edit scope.

Source review found no additional defect in the inspected final parsing paths.
Both final repeat implementations avoid changing the process-wide CSV limit.
This review was not a duplicate implementation: Astra inspected and checked;
Luna wrote and repaired the delegated code.

## Additional probe and reference limitation

The repeat solo implementation independently included a 150,000-character CSV
memo regression. After seeing that test, the supervising evaluator created
[a separate probe](replication/probe_large_csv.py) for bank and European CSV, with
quotes, embedded CRLF and an unterminated final record. The probe was applied
unchanged in fresh read-only processes to all four completed submissions and the
reference. Neither active trial agent received the probe or its results.

| Saved implementation | Additional large-memo probes |
| --- | --- |
| Original reference | 0/2 |
| First solo | 0/2 |
| First team | 0/2 |
| Repeat solo | 2/2 |
| Repeat team, after its own correction round | 2/2 |

The failing implementations returned `ValueError` for these valid CSV records.
The probe was not in the frozen suite and does **not** retroactively change its
scores. It does establish a previously untested contract failure in the original
reference and first pair. Their reported spending remains valid, but it is not
the measured cost of fixing this subsequently discovered defect.

The repeat team found and corrected the limit independently, before receiving any
external result. A future strengthened suite should include these cases and the
first pair's bare-CR/ignored-JSON-number cases, and requalify a corrected reference.
Do not patch the frozen reference in place or discard the failed probe receipts.

## What to improve next

Keep the current ownership and review policy for now. Both team runs saved money
with review and corrections included; both needed the coordinator to detect
behavior that the visible checker missed. Removing that review is not supported.

First strengthen the benchmark's executable coverage. Then test one small context
reduction: skip the model-selection guide when the user has already fixed the
worker model and effort. Both team coordinators loaded that 858-word guide despite
having an explicit Luna Max assignment. This is a candidate for a separate variant,
not a measured saving and not a reason to remove selection guidance from ordinary
deployment. No operational skill rule was changed in this repeat.

Two forced runs on one synthetic package still do not test automatic routing,
unguided delegation, other worker models or representative repository work.
The order was A then D in both pairs; there was no randomization or controlled
sampling/cache state. Broader conclusions require other tasks and configurations.

## Freeze and receipt details

The original source, policy, reference, grading cases and runner were reused
without changes. Preflight qualification passed again; effective prompt text
matched the first pair apart from fresh checkout paths. Codex remained 0.153.4.
Both conditions retained the same 1,200-second process limit and no automatic
retry. Frozen hashes and the copied team policy were checked after completion.

- Solo root: `01a08c4f-007f-7463-a46f-74c75ef84d82`.
- Team root: `01a08c54-3b50-7901-91b6-488fcdc95ee9`.
- Luna child: `01a08c54-c7cd-7a42-a44f-3946c1785e6e`.
- Source tree and entrypoint hash are identical to the first report.
- `replication/repeat.py` stores separate receipts under the original private
  fixture root's `replication-02` directory. It preserves the original guard and
  adds its own exclusive run guard and repeat-driver hash.
- `post-hoc-large-csv.json` retains all five extra-probe results. Raw sessions
  remain local; the runner's internal `C` label still means public condition D.
