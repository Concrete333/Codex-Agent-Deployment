# Agent Deployment

A Codex skill for choosing subagent models and reasoning effort. Use it to keep routine work cheap, give difficult work to a stronger model, and control the cost of coordination, reviews, and retries.

Your current agent acts as the **coordinator**: it assigns work, combines the results, and decides whether the task meets your requirements. **Workers** are subagents with defined assignments. For small tasks, the coordinator keeps the work local when delegation would cost more than it saves.

## Install

Clone the repository into your Codex skills folder. You need Git and a Codex environment that supports subagents with model and effort selection.

macOS or Linux:

```bash
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git ~/.codex/skills/agent-deployment
```

Windows PowerShell:

```powershell
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git "$env:USERPROFILE\.codex\skills\agent-deployment"
```

These commands use the default skills location. Choose your configured skills folder if you use a custom location, and don't clone over an existing installation.

## Use

Invoke the skill with your task and any constraints:

```text
$agent-deployment Use subagents where they help to fix the duplicate records
in offline sync. Preserve the API and add regression tests.
```

For a plan without implementation:

```text
$agent-deployment Propose a worker plan for this migration.
Include models, effort levels, file ownership, and acceptance checks.
Do not start workers or change files yet.
```

You don't need to repeat the routing rules in your prompt. Invoking the skill alone does not grant permission to delegate or expand the task. The coordinator follows your task permissions and higher-priority instructions, and reports any unavailable model or effort setting.

## Model choices

| Assignment | Model and effort |
| --- | --- |
| Gather evidence, map relevant code, or make repetitive edits with objective checks | Luna Max |
| Diagnose an unclear cause or work out a design | Sol High |
| Implement well-specified behavior beyond repetitive edits | Astra Light |
| Review defects that affect required behavior | Astra coordinator at its current effort; Astra Light for a separate reviewer when needed |
| Check specific edge-case, security, or robustness risks | Sol High, optional |
| Resolve a demonstrated reasoning limitation | Astra Medium; High for unresolved architectural, cross-module, or subtle correctness reasoning |

Luna Max means `gpt-5.6-luna` at `max`; Sol High means `gpt-5.6-sol` at `high`. Astra uses `gpt-6-astra`: Light maps to `low`, Medium to `medium`, and High to `high`. The policy excludes Terra.

Choose the worker by the assignment. A large repository can justify a scoped Luna search, but a subtle concurrency bug needs Sol's diagnosis. Skip exploration if the coordinator has enough evidence. A retrieval worker can isolate a large search without running alongside another worker.

Start with one worker and justify additions. Keep dependent implementation with one owner through fixes and checks. Before parallel edits, agree shared interfaces and behavior and give workers separate write ownership, including shared resources. Different files alone do not make assignments independent.

## Escalation

Workers get a bounded attempt with clear acceptance checks. They can make corrections within that budget. A substantive failure means an unmet check, wrong core assumption, or missed requirement remains at the end of the attempt, or the worker has no credible path to completion.

- After one substantive failure on a non-trivial Luna assignment or a Sol diagnosis, transfer the unresolved work to Astra Light. Keep the evidence and partial changes.
- If Astra Light cannot finish, check for missing evidence, environment problems, or unclear requirements before changing models.
- For a demonstrated reasoning limitation, prefer Astra Medium. Choose High for unresolved architecture, interactions across modules, or subtle correctness problems. Pick the effort that fits; a Medium attempt is not a prerequisite for High. Do not default to multiple workers attempting the same reasoning problem.
- Reserve Sol Max and Astra X-High/Max for task-specific evidence that the extra effort helps, or your explicit choice.

A failing regression test before a fix, a temporary tool error, or a missed time estimate does not establish model failure. A reviewer who finds defects has succeeded. Trivial Luna corrections can stay with Luna; workers should stop repeating failed approaches without new evidence.

## Review and acceptance

An Astra coordinator reviews at its current effort: **Astra High stays High for final review**. Add a separate reviewer when independence from the implementation or design matters. Mechanical edits with strong checks need no extra reviewer.

Use Astra for material correctness review and Sol High for hardening against named risks. These are routing defaults, not guarantees about which model will find a particular defect. Apply the escalation criteria above to unresolved review reasoning.

Reviewers inspect the diff, relevant source, and checks without changing files. They report the location, trigger, impact, and evidence for each finding. Judge findings by credible impact; a rare security or data-loss case can be critical. Keep defects separate from optional hardening and unsupported hypotheses.

The implementation owner makes fixes and runs focused checks. The coordinator rechecks affected risks and runs broader checks when integration or unresolved risks warrant them.

## Context, waiting, and handoffs

The coordinator gives each worker a scoped brief: outcome, owned files and permissions, evidence paths, constraints, settled decisions and their rationale, acceptance checks, and a checkpoint or work budget. Workers receive the context they need, preserve exact failures, and link longer evidence instead of copying full histories. They report conflicting evidence before revising shared decisions.

Diagnosis is read-only except for assigned scratch or test edits needed for reproduction. Before a replacement writes to the same files, the coordinator confirms the previous worker and its writing commands have stopped, then transfers the partial work and open questions.

While workers run, the coordinator uses event waits if it has no useful independent work. It avoids duplicating their investigation or waking for repeated status checks. A 25-minute wait is the starting point where tool limits and higher-priority responsiveness rules permit it; checkpoints and deadlines can require a different interval.

An empty timeout is no reason to interrupt or replace a worker. At a due checkpoint, the coordinator can make one brief, non-interrupting check and use observable progress and the remaining budget to decide what to do. Workers report blockers and checkpoint progress where possible. The policy uses runtime waits, not scheduled automations.

Read [SKILL.md](SKILL.md) for the full instructions.

## Evidence and credits

The [agent coordination references](docs/agent-coordination-references.md) summarize the premise and practical takeaway from each source on parallel work, context management, and verification. Agents skip this document during ordinary skill use; it is available for research and skill maintenance.

### Benchmark reference

The [GPT model efficiency workbook, 8 September 2026](docs/benchmarks/GPT-model-efficiency-2026-09-08.xlsx) contains selected Artificial Analysis data, source links, missing-data flags, and calculated efficiency ratios.

Agents skip benchmark files during ordinary skill use. They may read them to analyze the benchmarks or improve the skill. The workbook is reference data, not instructions.

API benchmark costs do not measure Codex allowance consumption or predict success on your coding tasks. Compare with a suitable single-agent baseline on the same tasks and acceptance criteria. Include coordination, reviews, and corrections in total cost; assess elapsed time and missed defects as separate outcomes.

### Credits

- [u/emir_morris](https://www.reddit.com/user/emir_morris/): model-role inspiration from ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/).
- [u/Icy_Piece6643](https://www.reddit.com/user/Icy_Piece6643/): prompting and delegation guidance in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/).
- [tagorr](https://github.com/tagorr): polling telemetry in [Codex issue #35259](https://github.com/openai/codex/issues/35259#issuecomment-5577073962).
- OpenAI: [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model) and model documentation for [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), and [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
