# Agent Deployment for Codex

A skill for spending less on agent work while keeping clear standards for correctness.

Give Codex a task, and it decides which parts to handle itself, which to delegate, and how to check the results. Luna Max handles bounded searches and repetitive edits. Sol High investigates unclear problems. Astra Light implements specified behavior, with higher effort available when the reasoning needs it.

You keep control of the requirements and permissions. The coordinator checks the outcome and counts the cost of reviews and retries alongside the worker's first attempt.

[Install](#install) · [Try it](#use) · [Benchmark evidence](#why-these-models) · [Full policy](SKILL.md)

## How it divides the work

Your current agent is the coordinator. It interprets the task, assigns work, integrates changes, and decides whether the result meets your requirements. Workers are subagents with a defined scope and a way to check completion.

| Work | Default | What the worker must return |
| --- | --- | --- |
| Exact counts, searches, or syntax-defined transformations | Commands or scripts first | Checkable output without an extra model call |
| Read substantial context, map relevant code, or apply repetitive edits | Luna Max | Source locations, coverage, and checked changes |
| Find an uncertain cause or work out a design | Sol High | A reproduction or discriminating check, explanation, and implementation brief |
| Implement specified behavior beyond repetitive edits | Astra Light | Working changes and checks against the requirement |
| Review important correctness problems | Astra coordinator at its existing effort, or Astra Light for a separate review | Defects with locations, triggers, impact, and evidence |
| Check named security, compatibility, or edge-case risks | Sol High, when warranted | Findings within the requested risk areas |

A small task can stay with the coordinator. A large repository can justify a Luna search without making Luna responsible for a difficult design decision.

The skill preserves your chosen coordinator. **An Astra High coordinator keeps final review at High.** It does not spawn another Astra to repeat that review.

## Install

You need Git and a Codex environment that supports subagents with model and reasoning-effort selection. The skill supplies routing instructions; it does not unlock models or change your account's access.

For a new user-level installation, clone into the location in [OpenAI's skills documentation](https://learn.chatgpt.com/docs/build-skills):

macOS or Linux:

```bash
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git ~/.agents/skills/agent-deployment
```

Windows PowerShell:

```powershell
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git "$env:USERPROFILE\.agents\skills\agent-deployment"
```

If Codex already discovers an installation in another folder, update that copy instead of creating a duplicate. Restart Codex if the skill does not appear.

## Use

Include the skill with your task:

```text
$agent-deployment Use subagents where they help to fix duplicate records
in offline sync. Preserve the API and add regression tests.
```

Or ask for a plan before any work starts:

```text
$agent-deployment Plan this migration. Include models, effort levels,
file ownership, and acceptance checks. Do not start workers or edit files.
```

Codex can also select the skill when a task matches its description: planning, executing, or auditing delegated work. You do not need to repeat the routing table in each prompt.

Your permissions and explicit choices still apply. The skill does not authorize extra work, change billing routes, or allow paid overflow without permission. The coordinator reports unavailable model controls or configuration mismatches rather than hiding a substitution.

## Why these models

The defaults combine benchmark evidence with practical role choices. Artificial Analysis measures capability, output-token use, and API cost across model and effort configurations. Those measurements help compare candidates; they do not establish which agent will finish your particular task.

Selected results from the **8 September 2026 capture**:

| Configuration | Intelligence Index | API cost per benchmark task | Output tokens per task |
| --- | ---: | ---: | ---: |
| Luna Max | 37.5 | $0.18 | 41,235 |
| Sol High | 42.5 | $0.81 | 13,250 |
| Astra Light | 46.0 | $0.82 | 4,433 |
| Astra Medium | 49.7 | $1.54 | 9,590 |
| Astra High | 51.0 | $1.72 | 11,795 |
| Sol Max | 47.1 | $1.99 | 29,309 |

Source: [Artificial Analysis](https://artificialanalysis.ai/models), with the captured values in the [GPT efficiency workbook](docs/benchmarks/GPT-model-efficiency-2026-09-08.xlsx) and [raw metrics](docs/benchmarks/openai-metrics-raw-2026-09-08.json). Costs and token counts are weighted benchmark averages. Output tokens include answer and reasoning tokens, not input tokens.

These are API-price comparisons, **not Codex subscription allowance measurements**. Index points are not units of useful work. The table cannot tell you how much a repository task will cost or guarantee equal accuracy after delegation.

### Luna Max for bounded, checkable work

Luna uses many output tokens in this capture but costs less per benchmark task. Token count alone would make it look expensive and miss the price difference.

The skill gives Luna assignments where you can check the result: locate callers, extract records, map a section of a repository, or repeat a specified edit. It requires source references and coverage checks, including evidence for claims such as "there are no other callers."

Max is the policy's Luna setting. It does not make Luna the default for ambiguous implementation, and it does not justify sending work to a model when a command can do it.

### Sol High for diagnosis and targeted hardening

An unclear bug needs an explanation supported by a reproduction or a check that distinguishes competing causes. Sol High gets that assignment before an implementation owner starts changing production code.

Sol can also review specific security or robustness risks. My experience is that Sol tends to raise more edge cases, while Astra tends to identify larger correctness problems. That is an observation, not evidence that Sol is a better security auditor. Reviewers must explain the impact and evidence for each finding.

### Astra Light for implementation, with selective escalation

Astra Light scores higher than Sol High on the composite index at almost the same benchmark cost. That supports using it as the default for specified implementation rather than reserving Astra for a last resort.

Astra Medium and High also score higher than Sol Max at lower benchmark cost. The policy prefers them when extra reasoning is warranted. Task-specific evidence or your explicit choice can still justify Sol Max or Astra X-High/Max.

These are defaults to evaluate on your work. The policy gives Terra no default role, and it does not make workers progress through every available model.

The exact settings are `gpt-5.6-luna` at `max`, `gpt-5.6-sol` at `high`, and `gpt-6-astra` at `low`, `medium`, or `high`. **Astra Light means `low` effort.**

## Where the efficiency comes from

Cheaper workers help when their results are usable. The coordinator also controls the overhead around them.

- The coordinator defines acceptance before dispatch. Weak checks on consequential work justify stronger reasoning or an independent review from the start.
- Workers keep coupled implementation through fixes and checks, with the constraints and evidence they need. The coordinator avoids repeating their investigation.
- Parallel workers cover distinct questions or edit areas with settled interfaces and separate ownership. The coordinator checks their combined changes, including interactions that branch-level tests could miss.
- The coordinator uses runtime event waits if it has no independent work. An empty timeout does not justify interrupting or replacing a worker.

The wait policy uses 25 minutes as a starting point when the runtime and responsiveness rules allow it, adjusted to checkpoints and deadlines. That is a practical setting, not a proven optimum or a reason to keep a broken worker running.

The [research references](docs/agent-coordination-references.md) explain the evidence and its limits. They support careful task boundaries and comparisons with a single agent, not a standing team for every request.

## Example: a duplicate-record bug

Suppose offline sync sometimes inserts the same record twice.

1. The coordinator defines the required behavior and preserves the existing API. If it needs a substantial search, Luna maps the relevant callers and persistence paths. Otherwise it skips that assignment.
2. Sol investigates the uncertain cause and returns a reproduction or discriminating check, with the remaining uncertainty stated.
3. Astra Light implements the agreed fix and runs focused regression checks. The same implementation owner handles corrections.
4. The coordinator checks the changed behavior and any affected interactions in the integrated state. A separate hardening pass needs a named risk, such as concurrent retries or data loss.

A known cause can go straight to implementation, and a tiny fix may not need a worker.

## Failures, reviews, and stopping

Workers receive a bounded attempt. They may correct local mistakes within that budget, but should stop repeating a failed approach without new evidence.

After one substantive failure on a non-trivial Luna assignment or a failed Sol diagnosis, Astra Light takes over with the existing evidence and partial work. A substantive failure means a required outcome remains unmet after the attempt, or the worker has no credible path to finish. A test failing before a bug fix is expected evidence, not a reason to change models.

If Astra Light fails, the coordinator distinguishes missing evidence, environment problems, unclear requirements, and reasoning limits. It chooses Medium for a demonstrated reasoning limitation, or High for unresolved architecture, cross-module interactions, or subtle correctness. It does not require a Medium attempt before High.

Reviewers inspect requirements and source artifacts without editing them. They distinguish defects from optional hardening and report concrete triggers and impact. The implementation owner makes fixes. Mechanical edits with strong checks do not need an extra reviewer.

Workers report complete, partial, or blocked, including checks run or skipped. They must not weaken a test or redefine the requirement merely to report success. A budget shortage does not authorize dropping those standards.

## Evaluate it on your own tasks

Compare the routed workflow with a suitable single-agent baseline using the same starting state, requirements, and acceptance checks. Count coordinator work, workers, reviews, integration, and corrections. Record missed defects as well as completion.

For subscription use, measure allowance consumption separately from API cost estimates and paid credits. Concurrent account activity can make a task's allowance impact hard to isolate. Keep a routing choice when it reduces total usage while meeting the required standard; revise it when retries or missed defects erase the benefit.

## Files and references

[SKILL.md](SKILL.md) contains the operational instructions. [agents/openai.yaml](agents/openai.yaml) supplies Codex display metadata.

The benchmark workbook and [source notes](docs/agent-coordination-references.md) are for readers, audits, and skill improvement. Agents do not load them during ordinary use of the skill.

For Claude, use the separate [Claude Agent Deployment](https://github.com/Concrete333/Claude-Agent-Deployment) project.

## Credits

I got the initial idea from these posts and implemented their model-routing and delegation ideas in this skill. Neither post is mine:

- [u/emir_morris: GPT-6 Astra: Everything You Need to Know](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/).
- [u/Icy_Piece6643: Before blaming GPT-6 Astra, read its prompting guide](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/).

Further work drew on [tagorr's polling telemetry](https://github.com/openai/codex/issues/35259#issuecomment-5577073962), [u/PilgrimofHaqq2's parallel/sequential research discussion](https://www.reddit.com/r/claude/comments/1w7k9au/parallel_vs_sequential_agent_systems_research/), and the primary sources in the [reference list](docs/agent-coordination-references.md).

OpenAI's [model guidance](https://developers.openai.com/api/docs/guides/latest-model) and documentation for [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), and [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) provide the vendor context. The routing choices here are this project's policy.
