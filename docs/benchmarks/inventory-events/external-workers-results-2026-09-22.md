# External worker comparison: GLM, DeepSeek and MiMo

Follow-up: a [single MiMo retry](mimo-retry-protocol-2026-09-22.md) repeated the
upstream timeout after 640 seconds with no edits. Its cost and outcome are recorded
separately and do not change the original comparison below.

DeepSeek V4.1 Flash Max and GLM 5.3 Flash Max both produced implementations that
passed all 27 independent test methods before Astra review. Astra High accepted
both without changing implementation code. MiMo again produced no implementation;
this time the API explicitly reported an upstream-provider timeout.

## Cost through acceptance

| Route | Worker reported cost | Astra acceptance/fallback | Captured total | Worker passed before review? |
|---|---:|---:|---:|---|
| DeepSeek V4.1 Flash Max + Astra High | $0.046131 | $0.538194 | **$0.584325** | Yes, 27/27 |
| GLM 5.3 Flash Max + Astra High | $0.071707 | $0.656320 | **$0.728027** | Yes, 27/27 |
| MiMo-V2.6-Pro Thinking + Astra High | $0.003448; incomplete | $0.686398 | **at least $0.689846** | No edits; Astra implemented the task |

All three final submissions passed 27/27 methods. MiMo's final pass belongs to
Astra's local implementation, not to the worker. Unknown usage from MiMo's failed
request means its captured total is a lower bound, not a full bill.

The [earlier same-task comparison](three-arm-results-2026-09-22.md) recorded
**$0.755888 for Astra High alone** and **$0.682504 for Luna Max + Astra High**.
Relative to those historical runs:

- DeepSeek's pipeline cost **22.70% less than solo** and **14.39% less than Luna's pipeline**.
- GLM's pipeline cost **3.69% less than solo**, but **6.67% more than Luna's pipeline**.

These are single observations, not a model ranking. There was no fresh solo or
Luna control in this batch. Prices are API-equivalent Codex estimates plus Kilo
reported costs, not subscription bills or quota savings. Shared preparation,
supervision and analysis are excluded. The apparently low captured MiMo total
is not evidence of useful delegation: Astra did the whole implementation, and
its cost varied from the earlier solo run.

## Work and review

DeepSeek wrote the three component modules and 34 focused tests. Astra added
four acceptance tests; the final public/worker/acceptance suite passed 42 tests.
File comparisons confirm that Astra changed neither the worker's implementation
nor its existing tests. Acceptance accounted for **92.11%** of pipeline cost.

GLM wrote the three modules and 71 focused tests. Astra added three acceptance
tests; the final combined suite passed 78 tests. No worker implementation or
existing tests changed during acceptance. Acceptance accounted for **90.15%**
of pipeline cost. Its larger test suite is not evidence of higher accuracy;
both submissions passed the same independent grader.

MiMo completed two reading/tool responses, then exited 1 after 628.63 seconds.
There were no edits, tests or valid handoff. Astra implemented all three modules
and nine tests; its combined public/added suite passed 13 tests.

All final candidates passed the frozen independent grader again during this
offline audit. Its 27 methods include an 80-scenario lifecycle matrix within one
method. Correct controls passed and the starter plus nine defective variants
failed before inference. Private grades were not supplied to task models.

## What the MiMo failure tells us

The terminal API error was:

```text
503: The upstream provider timed out while sending the response.
type: timeout
request id: lhr1:lhr1::np562-1790073414115-5e119aa55c3a
```

This arrived before our 30-minute worker timeout. There was no step cap, no
recorded generation-length stop, and no permission or handoff-validation error
preceding the API failure. The last completed response ended with `tool-calls`.
Our wrapper retained the error and rejected the attempt after Kilo exited.

This attempt failed at the service boundary, with an explicit upstream timeout.
The logs do not establish whether Kilo's gateway or the upstream service set the
timeout, or why the provider could not finish. They also do not establish that
the previous `AI_InvalidResponseDataError` had the same cause. GLM and DeepSeek
succeeded through the same wrapper, so the wrapper is not generally preventing
implementation; model-specific route or protocol problems remain possible.

The separate earlier 32k generation-length failure was a Kilo output ceiling.
This experiment kept the 65,536 per-response override already used in the prior
inventory attempt. Raising it further or removing another local limit is not
a demonstrated remedy for an upstream timeout. A provider investigation can use
the request ID above; distinguishing clients would require a separate controlled
test against the same model/provider route. No further paid retry was started.

## Configuration and accounting checks

Kilo 7.7.7 exposed MiMo `thinking` (reasoning enabled, high), GLM `max` and
DeepSeek `max`. These are the highest variants its catalogue exposed for the
requested models. Preflight and resolved agent profiles match each requested
model/variant with uncapped steps. Provider-internal compliance is not observable.
All workers had the same 65,536 output ceiling, normal implementation tools,
compaction and 30-minute timeout. Global defaults were not changed.

All Astra sessions record `gpt-6-astra/high`; own-response usage reconciles to
their cumulative counters. Rates match the prior comparison: $10 uncached input,
$1 cached input and $50 output per million tokens. No cache writes or long-context
pricing threshold applied. Kilo cost equals the sum of unique completed-step
cost events; missing failed-request usage remains unknown.

| Astra stage | Input including cache | Cached input | Output including reasoning | Reasoning | Responses |
|---|---:|---:|---:|---:|---:|
| DeepSeek acceptance | 151,190 | 121,984 | 2,483 | 357 | 7 |
| GLM acceptance | 213,093 | 176,640 | 2,303 | 435 | 9 |
| MiMo fallback implementation | 128,590 | 102,528 | 6,465 | 645 | 7 |

End-to-end elapsed times were 4.7 minutes for DeepSeek, 12.4 for GLM and 14.3 for
MiMo plus fallback. Concurrent execution and provider conditions limit timing
comparisons. No model waiting/polling calls appeared in the audited Astra sessions.
Worker ownership was resolved, all worker locks were absent, and native acceptance
processes exited zero without timeout. The batch supervisor saved its terminal
receipt and queued one completion notification.

## Takeaway and retained evidence

DeepSeek and GLM are viable candidates for this settled component. DeepSeek had
the lowest observed cost; review still dominated both successful routes. These
clean passes do not justify removing substantive review or a universal model
ranking. DeepSeek Max is adopted as the configurable Kilo default at the user's
request; broader task reliability remains unmeasured. MiMo through the current route remains unreliable in
these attempts; this is not a demonstrated failure of its coding ability.

See the [protocol](external-workers-protocol-2026-09-22.md). The ignored
`local-external-workers.json` locates the retained batch directory
`inventory-external-6000de3a10674d3daa12457d68d00f50`. `accounting.json` contains
receipts, reconciled usage, grades and file comparisons. Reproduce the offline
audit with `three_arm_analysis.py --root <retained-batch-directory>`.

| Worker | Kilo run | Astra session |
|---|---|---|
| DeepSeek | `20260922-113601-909ea5ea` | `01a0c8b2-d8e6-7593-ada8-14531e37bed2` |
| GLM | `20260922-113555-d7f0d8f4` | `01a0c8b9-ed3d-7ae0-b2c0-5b2a4900099d` |
| MiMo | `20260922-113549-0671011e` | `01a0c8b9-d21c-7630-b0f5-ebcd46ee4d58` |
