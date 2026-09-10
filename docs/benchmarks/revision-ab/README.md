# Revised-skill A/B diagnostic evaluation

Three fresh, purpose-built task shapes compare Astra High alone with Astra High
using the revised deployment skill. These are diagnostic fixtures, not standard
benchmarks or a representative sample of production repositories.

[Results: 10 September 2026](results-2026-09-10.md).

| Report condition | Shared runner argument | Configuration |
| --- | --- | --- |
| A: solo baseline | `A` | No deployment skill; delegation disabled |
| B: revised skill | `C` | Frozen skill; Luna, Terra, Sol and authorized Opus 5 available; delegation optional |

The runner's historical `B` means unguided delegation and is **not used here**.

## Tasks and acceptance

- **Repair:** compact half-open integer ranges without mutating input. Thirteen
  external test methods include 300 seeded point-set comparisons, malformed
  inputs, touching/nested ranges, generators and frozen-file checks. A separate
  endpoint-sweep reference passes; the seeded implementation fails.
- **Investigation:** audit 120 services for production email exports without a
  valid waiver. Approximately 148 KB of catalogue records join profiles, field
  overrides, ownership and dated Markdown waiver records. Acceptance requires
  exact findings, owner/reason, coverage reconciliation, relevant file/line
  citations and unchanged source evidence. A separately implemented reader
  matches the generator's oracle; four deliberately wrong reports are rejected.
  This structured corpus permits scripting: delegation is not forced, and the
  corpus size is not the amount of context an efficient solver must load.
- **Component:** deliver a tenant-scoped idempotency ledger within a small
  event-ingestion package, including integration and regression tests. The
  [component contract](component/task/TASK.md) defines behavior and scope; its
  independent checks cover replay, conflicts, expiration, failures, mutation,
  validation and existing callers. This is a modest multi-module fixture, not
  a large real-world repository.

Workers get the complete contract, starting implementation and public smoke
tests, but not external checks, reference solutions or other trial artifacts.
Grading is read-only. File access is instruction-constrained, not an adversarial
security boundary. Frozen task evidence and existing tests cannot be altered.

## Controls

- Same Astra High coordinator, local CLI, runtime and task within each pair.
- Fresh checkouts; personal skill discovery, plugins and memory disabled.
- Six **sequential** runs: repair A/B, investigation B/A, component A/B.
- Same 45-minute safety limit for every run; elapsed time is not a score.
- Skill, references, wrapper, sources and graders hashed before launch. No skill
  edits or automatic model retries during the experiment.
- Skill condition permits native workers and the existing Claude subscription
  through the frozen wrapper. No API credentials, billing changes or paid
  overflow are authorized. The environment may still prevent a provider route;
  report such failures rather than silently treating the route as tested.
- Native workers share the tested environment and must use supported explicit
  configurations. Provider availability does not require delegation.
- Cache state, sampling and service load remain uncontrolled. One run per cell
  is diagnostic only. Repeat promising or surprising comparisons before claiming
  a reliable improvement.

## Run

From the repository root, after explicit authorization for model calls:

```powershell
python -B -X utf8 docs/benchmarks/revision-ab/prepare.py
python -B -X utf8 docs/benchmarks/revision-ab/batch.py
python -B -X utf8 docs/benchmarks/revision-ab/summarize.py
```

Preparation is local and does not call models. It creates a unique system-temp
fixture and skill snapshot; the ignored `local-fixture.json` points to them.
The batch uses the existing pilot runner, records a frozen input manifest and
refuses automatic reruns. A result or harness failure is retained without
spawning a replacement model. The safety cutoff preserves and grades partial
artifacts separately from successful workflow completion.

Source generation, graders, references and scripts are public in this folder.
Raw rollouts, generated answers, receipts, private paths and full error logs
remain outside the repository. Do not give this folder to trial participants.

## Interpretation

Compare acceptance and whole-run cost together, not worker price or number of
tests written. Read parent and child rollouts, reconcile unique response usage
with own-thread cumulative counters, and include any Claude worker receipts.
Record coordinator input volume, responses, handoffs, waiting, repair and
verification activities. Separate observed activity from causal attribution.

API-equivalent estimates use published standard rates, not subscription quota
or actual account charges. Reasoning output is already included in output.
Timed-out requests can have unrecorded in-flight usage. Preparation, supervisor
messages and offline evaluation are outside participant totals; they are real
experiment overhead, not savings attributed to the skill.

The preparation helper is Sol High and is not a trial worker. All paid trials
remain isolated from its context and reference implementation. Official runner
controls: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Rate references: [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol).
