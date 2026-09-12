# Prose migration-review A/C diagnostic

[A/C results](results-2026-09-10.md) · [Forced Luna result](results-forced-luna-2026-09-10.md) · [Sol review result](results-sol-review-2026-09-10.md) · [Semantic review](semantic-review.md).

[Opus builder and reviewer results](results-opus-pair-2026-09-10.md).

This pair tests whether a cheap worker can replace substantial source reading
and answer writing without making the coordinator repeat it. It is a synthetic
extraction/review task, not a coding benchmark or representative production sample.

Fifty independent discussions concern a fictional Harbor 4.0 migration. Each
asks whether one concrete user action is needed. Participants must interpret
scope, release decisions, proposals, withdrawals and unresolved evidence, then
produce one concise, cited record per discussion. Scripts remain allowed. There
is no requirement to read every byte into model context or to delegate.

| Condition | Configuration |
| --- | --- |
| A | Astra High; no deployment skill; delegation disabled |
| C | Astra High; unchanged current skill; delegation optional; Luna, Terra, Sol and authorized Opus 5 available |

An additional, explicitly authorized **D control** uses the same C configuration
and frozen task/skill, appending only this 41-word instruction:

> Required execution: use the supplied skill. Delegate the complete TASK.md deliverable to one gpt-5.6-luna worker at max effort with fork_turns="none". Keep the assignment brief; the worker owns reading, answer writing and local checks. Retain final verification. Do not launch other workers.

`forced_luna.py` creates a local runner snapshot with one prompt-append line;
it does not change the original runner, skill or A/C receipts. Preflight verifies
that the base prompt, runtime settings, task tree, policy and grader match C.
The D result tests explicit delegation, not the skill's spontaneous routing.

```powershell
python -B -X utf8 docs/benchmarks/prose-migration/forced_luna.py prepare
python -B -X utf8 docs/benchmarks/prose-migration/forced_luna.py run
python -B -X utf8 docs/benchmarks/prose-migration/forced_luna.py summarize
```

### Review-only diagnostic

`review_only.py` gives one Sol High reviewer the saved **initial**, uncorrected
Luna answer from D, the original `TASK.md`, and all 50 source discussions. The
answer is reconstructed from D's retained initial-answer command output, not
the corrected final file. Its parsed contents are preserved; JSON formatting is
normalized and separately hashed. No gold labels, known findings, other trial
results or routing documents are supplied to the reviewer.

The reviewer runs read-only with delegation disabled, using the prior solo
runner's isolation settings and a 45-minute cutoff. Its assignment requests full
coverage and evidence-backed material findings, without suggesting that defects
exist or requesting a finding count. The current skill guides assignment and
review ownership; this is a worker capability test, not a full skill/no-skill
comparison. Preflight checks source identity, input readability and discovery
suppression before inference. Only `run` starts a paid session, once.

Evaluate findings against the original sources: distinguish substantive errors,
missing action details, unsupported corrections and stylistic preferences. Check
the three issues previously identified by Astra, but accept additional valid
findings rather than treating that set as an exhaustive answer key. Require
coverage evidence and report omissions. Do not reveal expected findings in a
follow-up or retry the reviewer. No repair pass is included in this diagnostic.

```powershell
python -B -X utf8 docs/benchmarks/prose-migration/review_only.py prepare
python -B -X utf8 docs/benchmarks/prose-migration/review_only.py run
python -B -X utf8 docs/benchmarks/prose-migration/review_only.py summarize
```

Captured Sol usage measures only this review. Preparation, evaluator work,
coordinator dispatch/acceptance and any future corrections are excluded; do not
present a cheaper reviewer as measured end-to-end savings.

### Opus builder and reviewer diagnostics

`opus_pair.py` prepares two separate checkouts and runs two fresh Opus 5 Low
sessions sequentially through the existing Claude wrapper. The builder receives
only the original task and sources and owns the entire answer, self-checks and
local corrections. The reviewer receives the same initial Luna answer as Sol,
the original task and all sources, with no known findings or gold. Neither gets
the other's output or the routing policy.

The builder's edit profile permits local shell checks; the reviewer uses the
wrapper's Read/Glob/Grep-only profile and must report checks it cannot execute.
Its prompt supplies the input file hash rather than asking it to invent one.
External structural grading and source-based evaluation remain unchanged. This
tool difference from Sol's shell-enabled review limits a model-only comparison.

Each job has a 45-minute cutoff and a $5 API-equivalent safety cap, not a
subscription-allowance ceiling. No automatic retry or billing fallback is
permitted. Version/authentication and inherited-context checks precede dispatch.
The wrapper uses five-minute caching, disables skill discovery and configured
MCP servers/settings sources, and preserves Claude's default coding prompt.
It is not an operating-system sandbox. Existing global Claude instructions were
inspected; exact primary source text is required for these assignments.

```powershell
python -B -X utf8 docs/benchmarks/prose-migration/opus_pair.py prepare
python -B -X utf8 docs/benchmarks/prose-migration/opus_pair.py run
```

These are worker-only capability diagnostics. Claude receipts exclude the
supervisor's preparation and acceptance, and do not measure a complete Astra-led
workflow. Full saved answers require semantic review, even after all automated
checks pass. Requested effort and reported model identities are recorded
separately; the wrapper does not independently verify effective effort.

For the original A/C pair, the task never names a preferred worker. C receives the same skill
and provider authorization used in the previous diagnostic. Workers, if any,
must be chosen by that participant. Execution is sequential, A then C, with the
same 45-minute safety cutoff; a timeout is partial, not completion. No automatic
trial retries or policy changes are permitted during the pair.

## Evidence and checks

`cases.json` contains authored source material and an author answer key, outside
the participant checkouts. A separate source-only review records dispositions
before comparing against that key. Ambiguities must be resolved before freezing
the inputs, with the preflight review recorded in `source-audit.json`.

`grade.py` checks all 50 dispositions, ID coverage/order, release/date, schema,
quote accuracy and line bounds, answer length limits, and source preservation.
Exact coverage of the author's preferred evidence passages is only a diagnostic:
equivalent sufficient citations are valid. A separate semantic review must
check every submitted explanation and its supporting quotes against the source;
the automated score alone does not establish faithful action/scope advice.

The author reference must pass. Deliberately omitted records, wrong decisions,
fabricated quotes, invalid line ranges, wrong dates and changed sources must fail. Before model
runs, execute reference grading through the actual read-only sandbox and inspect
both participant prompts for accidental source/key/skill exposure. Access is
instruction-constrained, not an adversarial confidentiality boundary.

`experiment.py` reuses the existing pilot runner and revision accounting code.
Preparation snapshots the skill and renders only the task and 50 source files.
It creates ordinary inherited-permission temporary directories to avoid the
private-temp access failure encountered in the previous evaluation. Local paths,
answers and raw rollouts remain private; `local-fixture.json` is ignored by Git.

```powershell
python -B -X utf8 docs/benchmarks/prose-migration/experiment.py prepare
# Finish source-audit.json and the sandbox/prompt preflights before run.
python -B -X utf8 docs/benchmarks/prose-migration/experiment.py run
python -B -X utf8 docs/benchmarks/prose-migration/experiment.py summarize
```

`experiment.py run` launches the original two paid/subscription-backed sessions;
`forced_luna.py run` launches one additional, separately authorized D control.
The other modes make no model calls. Preparation
of the prose by Sol High, independent review, supervision and offline evaluation
are experiment overhead and excluded from participant comparisons; report the
fixture-author cost separately where telemetry permits.

## Interpretation

Compare complete parent-plus-worker API-equivalent cost and acceptance together.
Inspect whether source context and answer generation actually moved to a cheaper
worker, or whether the parent reproduced them. Count repairs and verification,
check effective model/effort, and reconcile unique response usage against thread
counters. API estimates are not subscription charges or allowance consumption.

One run per condition cannot establish reliable savings or a new model ranking.
Synthetic prose may be easier or more regular than real issue discussions. This
is a deliberately favorable opportunity for context-isolating delegation, not an
estimate of its average value. If C stays solo, report that routing decision;
do not silently force a worker or keep changing the task until delegation wins.

The frozen rates are the existing runner's standard-rate assumptions, checked
against official [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
and [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) documentation.
Runtime configuration follows [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
