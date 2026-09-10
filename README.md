# Agent Deployment for Codex

Delegate work your coordinator can stop doing—not work it will have to do again to check the answer. Use Luna, Terra, Sol or Opus 5 when a bounded assignment can reduce total cost, and keep hard, coupled reasoning with your current Codex agent.

This skill helps your current Codex agent decide **whether to delegate, which model and effort to use, and how to accept the result**. It offers starting recommendations rather than assigning every kind of work to a fixed model. A small task can stay with the coordinator; a difficult task does not automatically need a team.

[Install](#install) · [Use](#use) · [Model guide](references/model-selection.md) · [Evidence](docs/model-performance-comparison.md)

## How it works

Your current agent remains the coordinator. It owns the required outcome and cross-cutting decisions, chooses workers when they help, integrates changes and makes the final acceptance decision. Workers own local implementation choices within their assignments.

| Before a worker starts | While it works | Before accepting the result |
| --- | --- | --- |
| Identify work removed from the coordinator and how to check it. Then choose a worker and define ownership and done. | Keep coupled implementation, tests and fixes together. Avoid duplicate investigation and unnecessary status polling. | Check the agreed behavior and affected interactions. Finish when acceptance is supported; reopen for new evidence or required review. |

Worker choice is flexible within four families: **Luna, Terra, Sol and Opus 5**. Astra and Fable are not worker options. The coordinator cannot lower the acceptance standard to fit a budget.

**Your coordinator keeps its model and effort.** An Astra High coordinator handles difficult reasoning and final acceptance itself. It does not spawn another Astra to do that work.

## Choosing models

The [model-selection guide](references/model-selection.md) explains when each worker is useful, which effort to start with, and how to compare the cost of a checked result. An allowed model is not automatically a worthwhile delegation.

A few starting points:

| Work | Starting candidate |
| --- | --- |
| Bounded extraction, source mapping or pattern-following edits with objective checks | Luna Max |
| Bounded native implementation with settled interfaces and regression checks | Terra Max |
| Supplied analytical or scientific subproblem | Sol Low/Medium |
| Bounded diagnosis, analysis or independently justified review | Sol High |
| Bounded implementation through an authorized Claude subscription | Opus 5 Low |
| Open-ended diagnosis, architecture, difficult coupled work and final judgment | Current orchestrator; no worker |

These are alternatives, not a sequence. **Luna uses Max only.** Terra Max is the starting candidate for native implementation; lower effort is not assumed sufficient. Sol and Opus may use more effort for a concrete bounded reasoning need, but not to outsource work that belongs with the orchestrator.

Choose Luna when the job mostly finds evidence or follows a fixed pattern. Choose Terra when implementation needs more local judgment. Sol fits supplied problems requiring derivation or evaluation. Opus 5 offers a Claude implementation route when its account access, retained context or task results justify the setup.

For scale, captured suite-average costs are $0.18 for Luna Max, $0.50 for Sol Medium, $1.10 for Opus 5 Low and $1.40 for Terra Max. These are not prices for your particular assignment. Compare the worker, preparation and review together against keeping the work local; lowering effort does not itself lower a model's per-token price.

“Accepted” means the requested outcome is supported by appropriate evidence: reconciled source coverage for extraction, a discriminating reproduction for diagnosis, or behavior and integration checks for implementation. A worker reporting completion is not enough.

The goal is lower total cost while meeting the required correctness standard, not faster completion. The choice depends on uncertainty, available checks, the consequences of a missed defect, context already held by a worker and your authorized account preferences. Commands and scripts come first for exact work that does not need another model.

Claude is optional. Using two providers is not a goal in itself, and a provider switch does not automatically improve a result.

## Install

You need Git and a Codex environment that supports subagents with explicit model and reasoning-effort selection. The skill supplies instructions; it does not unlock models or change account access.

For a new user-level installation, use the skills location in [OpenAI's documentation](https://learn.chatgpt.com/docs/build-skills).

macOS or Linux:

```bash
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git ~/.agents/skills/agent-deployment
```

Windows PowerShell:

```powershell
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git "$env:USERPROFILE\.agents\skills\agent-deployment"
```

If Codex already discovers an installation elsewhere, update that copy instead of creating a duplicate. Restart Codex if the skill does not appear.

## Use

Include the skill with your task:

```text
$agent-deployment Use subagents where helpful to fix duplicate records
in offline sync. Preserve the API and add regression tests.
```

To allow Claude workers:

```text
$agent-deployment You may use my installed Claude CLI and subscription
for this task. Choose appropriate models and efforts, and verify the result.
Do not enable paid overflow.
```

For a plan only:

```text
$agent-deployment Plan this migration. Include models, efforts, ownership
and acceptance checks. Do not start workers or edit files.
```

Codex can select the skill when a request matches its description. Explicitly naming it is the clearest way to request it. Skill selection does not itself authorize delegation, edits or additional spending.

## Claude CLI workers

Codex calls your installed Claude Code CLI through the included Python wrapper—no MCP server required. The wrapper accepts only Opus 5, with explicit effort, read-only or editing profiles, session resumption and bounded batches of independent workers.

Requirements: Python 3.10+, Claude Code 2.1.108+ and a logged-in Claude subscription with access to the selected model. The wrapper supports `low`, `medium`, `high`, `xhigh` and `max`; the selected model and installed CLI must support the requested setting.

Workers use five-minute caching and disabled skill discovery while retaining Claude's default coding prompt. The wrapper requests no automatic model fallback or API billing fallback. Compact results link to complete local receipts.

See [the Claude CLI guide](references/claude-cli.md) for setup, request format, permission profiles and continuation.

Important limits:

- Tool restrictions are not an operating-system sandbox. The target repository and inherited Claude context must be trusted.
- Usage receipts contain estimates, not remaining subscription allowance. The wrapper cannot disable account-side paid overflow.
- A successful CLI exit is not accepted work. The coordinator still checks results, artifacts and unresolved risks.
- Concurrent editing jobs need separate checkouts and independent shared state. A worker timeout terminates work; a coordinator wait timeout does not.

## Where the savings should come from

The first decision is whether to delegate at all. The coordinator identifies a bounded workload it can hand over and a way to check the result without repeating it. If preparation, checking and likely repairs erase the benefit, it works locally without loading the model guide.

A repository search can spare the coordinator a large amount of source context. A settled component can give a worker useful ownership of implementation, tests and corrections. Splitting tightly coupled work between an implementer and a test writer may instead make both agents learn the same behavior and leave the coordinator to reconcile them. Independent test design or review is useful when it addresses a specific risk.

“Write tests” is not automatically cheap work. Extending a known fixture with agreed expected results is different from discovering which regression cases expose unfamiliar behavior. Model choice follows the uncertainty, not the type of file being written.

The coordinator settles consequential decisions and defines required behavior and checks without writing the whole solution for a worker. It verifies evidence and affected interactions, then finishes when acceptance is supported. New evidence can reopen the work; optional hardening does not automatically extend the task. Acceptance standards cannot be weakened to save money.

Workers receive focused assignments and return concise evidence, not their entire investigation. The coordinator does not duplicate active worker work. It uses supported completion waits instead of repeated status checks; if suitable waiting is unavailable, it keeps the work local or reports the limitation.

A substantive non-trivial Luna failure ends that Luna attempt. The coordinator preserves useful work and chooses local completion or a revised assignment deliberately—there is no mandatory model ladder.

## What the evidence does—and does not—show

The [combined reference](docs/model-performance-comparison.md) contains 38 GPT and Claude configurations from the 8 September 2026 Artificial Analysis capture: capability, benchmark-task cost, token use, coding, long-context and knowledge metrics. The [analysis notes](docs/model-selection-analysis.md) interpret the wider model evidence; they are not the current worker allowlist.

These are **API-priced benchmark comparisons, not subscription allowance measurements**. The cost column is a suite-wide average, not the cost of each individual evaluation. Composite scores do not establish which model will finish a particular repository task. Small score differences are not a reliable basis for a universal ranking.

The [research references](docs/agent-coordination-references.md) support careful task boundaries, verification and comparisons with simpler approaches. They do not establish that a standing team is cheaper or more accurate than one capable agent.

To evaluate the skill, compare the same tasks with a single agent, unguided delegation and skill-guided delegation. Keep starting states, acceptance checks and relevant configurations controlled. Count preparation, workers, reviews, failed attempts and integration; report acceptance rate and total spending per accepted result together. Repeat trials and test configuration changes one at a time. Measure each provider's allowance consumption separately from API estimates. Our local trials have **not demonstrated savings from the skill**. Solo was cheaper in the [initial repair comparison](docs/benchmarks/dual-service/results-2026-09-09.md). In the later [cattrs feature test](docs/benchmarks/cattrs-self/results-2026-09-10.md), solo completed for $1.44 API-equivalent, unguided delegation for $2.45, and skill-guided delegation reached its safety timeout after at least $3.02. All saved implementations passed the external checks, but the timed-out workflow remained partial.

In that cattrs run, the Luna worker cost about $0.05 and the coordinator $2.97. Native waiting worked without a polling loop. These observations motivated the current emphasis on workload ownership and bounded verification; they do not prove the revised guidance saves money. The trials are small, implementations varied, and the external checks establish a correctness floor rather than identical behavior on every input.

## What agents load

| File | Purpose | Loaded during ordinary deployment? |
| --- | --- | --- |
| [SKILL.md](SKILL.md) | Scope, ownership, verification, continuation and waiting | When the skill is selected |
| [Model-selection guide](references/model-selection.md) | Model comparisons, relative costs and effort choices | Only after deciding delegation is useful |
| [Claude CLI guide](references/claude-cli.md) | How to invoke and manage Claude workers | For Claude delegation only |
| [Combined evidence](docs/model-performance-comparison.md), [analysis](docs/model-selection-analysis.md), workbooks and [research](docs/agent-coordination-references.md) | Audits and skill improvement | No |

Workers receive their assignment and relevant project evidence—not the entire routing guide or benchmark collection. Audits and maintenance may read the relevant material in `docs/`.

For a Claude Code coordinator instead of Codex, see [Claude Agent Deployment](https://github.com/Concrete333/Claude-Agent-Deployment).

## Credits

I got the initial idea from these posts and implemented their model-routing and delegation ideas in this skill. Neither post is mine:

- [u/emir_morris: GPT-6 Astra: Everything You Need to Know](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/).
- [u/Icy_Piece6643: Before blaming GPT-6 Astra, read its prompting guide](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/).

Further work drew on [tagorr's polling telemetry](https://github.com/openai/codex/issues/35259#issuecomment-5577073962), [u/PilgrimofHaqq2's parallel/sequential research discussion](https://www.reddit.com/r/claude/comments/1w7k9au/parallel_vs_sequential_agent_systems_research/), and the primary sources in the [reference list](docs/agent-coordination-references.md).

Model evidence comes from [Artificial Analysis](https://artificialanalysis.ai/models), with vendor context from [OpenAI](https://developers.openai.com/api/docs/guides/latest-model) and [Anthropic](https://platform.claude.com/docs/en/models/fable-5-1/overview). The deployment recommendations are this project's interpretation, to be tested against real accepted outcomes.
