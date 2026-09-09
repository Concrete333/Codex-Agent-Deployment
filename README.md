# Agent Deployment for Codex

Choose suitable GPT or Claude workers, give them bounded assignments, and check their work without spending more on coordination than the task needs.

This skill helps your current Codex agent decide **whether to delegate, which model and effort to use, and how to accept the result**. It offers starting recommendations rather than assigning every kind of work to a fixed model. A small task can stay with the coordinator; a difficult task does not automatically need a team.

[Install](#install) · [Use](#use) · [Model guide](references/model-selection.md) · [Evidence](docs/model-performance-comparison.md)

## How it works

Your current agent remains the coordinator. It owns the required outcome and cross-cutting decisions, chooses workers when they help, integrates changes and makes the final acceptance decision. Workers own local implementation choices within their assignments.

| Before a worker starts | While it works | Before accepting the result |
| --- | --- | --- |
| Define scope, permissions and checks. Choose a suitable model and effort. | Keep dependent changes with one owner. Avoid duplicate investigation and unnecessary status polling. | Inspect evidence and changed behavior. Check interactions after integration. Count corrections and reviews as part of the cost. |

The skill separates flexible model choices from firm requirements. The coordinator can choose a different suitable model; it cannot lower the acceptance standard to fit a budget.

**Your coordinator keeps its model and effort.** An Astra High coordinator still performs final acceptance at High. There is no mandatory second Astra reviewer.

## Choosing models

The [model-selection guide](references/model-selection.md) explains each model's useful strengths, relative cost, effort choices and the evidence needed to accept its work. It includes direct comparisons: when Luna's low cost is useful, when Opus can justify its premium, where Sol fits, and when Fable's specialist capabilities are worth paying for.

A few starting points:

| Work | Starting candidate |
| --- | --- |
| Bounded extraction, source mapping or pattern-following edits with objective checks | Luna Max |
| Specified implementation or bounded diagnosis with dependable checks | Astra Light |
| Difficult diagnosis, coupled changes or subtle correctness review | Astra High |
| Hard repository reasoning needing more effort | Astra X-High |

These are alternatives, not a sequence. Astra Medium remains an option when adequate. **Astra Light means `gpt-6-astra` at `low` effort. Luna uses Max.** Final acceptance stays with the coordinator; the table does not require a separate reviewer.

Sol Low/Medium are candidates for bounded scientific Python work with executable checks. Sol and Fable have specialist uses in demanding scientific or professional work. Fable X-High is not a routine general-coding upgrade.

For scale, the captured suite-average costs are $0.18 for Luna Max, $0.82 for Astra Light, $1.10 for Opus Low and $5.98 for Fable X-High. These are not prices for your particular assignment. A premium makes sense when it buys needed capability or avoids expensive checking and rework—not simply because a model is stronger overall.

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

Codex calls your installed Claude Code CLI through the included Python wrapper—no MCP server required. It supports explicit model and effort, read-only or editing profiles, session resumption and bounded batches of independent workers.

Requirements: Python 3.10+, Claude Code 2.1.108+ and a logged-in Claude subscription with access to the selected model. The wrapper supports `low`, `medium`, `high`, `xhigh` and `max`; the selected model and installed CLI must support the requested setting.

Workers use five-minute caching and disabled skill discovery while retaining Claude's default coding prompt. The wrapper requests no automatic model fallback or API billing fallback. Compact results link to complete local receipts.

See [the Claude CLI guide](references/claude-cli.md) for setup, request format, permission profiles and continuation.

Important limits:

- Tool restrictions are not an operating-system sandbox. The target repository and inherited Claude context must be trusted.
- Usage receipts contain estimates, not remaining subscription allowance. The wrapper cannot disable account-side paid overflow.
- A successful CLI exit is not accepted work. The coordinator still checks results, artifacts and unresolved risks.
- Concurrent editing jobs need separate checkouts and independent shared state. A worker timeout terminates work; a coordinator wait timeout does not.

## Where the savings should come from

Choosing a cheaper model is useful only when the result meets the requirement. This skill also limits the work around that first attempt.

The coordinator settles consequential behavior and interface choices before assigning their implementation. It asks what could invalidate the approach and whether the checks would catch that failure. Workers get those decisions, a bounded assignment and a concrete definition of done—not a request to rediscover the plan.

That can make a small implementation suitable for Luna, even inside a complicated project. It does not make Luna suitable for every well-described task. Preparation, checking and repairs count too; if they cost more than keeping one capable owner, delegation has not saved anything. A short assignment is usually enough, without creating extra planning documents.

Coupled implementation stays with one owner through corrections. Independent reading can be split to reduce context burden; independent writing requires settled interfaces and ownership.

Extra review needs a reason. Reviewers report concrete defects and impact, not a target number of findings. The coordinator checks the integrated result without automatically repeating every investigation or test suite.

When a worker is still running, the coordinator uses suitable runtime waits instead of repeatedly waking to ask for status. An empty timeout is not evidence that the worker should be replaced.

If an attempt fails, the coordinator distinguishes missing evidence, environment problems and unclear requirements from a reasoning limit. It preserves useful work and chooses the next step deliberately. A substantive non-trivial Luna failure ends that Luna attempt; there is no mandatory ladder through every other model.

## What the evidence does—and does not—show

The [combined reference](docs/model-performance-comparison.md) contains 38 GPT and Claude configurations from the 8 September 2026 Artificial Analysis capture: capability, benchmark-task cost, token use, coding, long-context and knowledge metrics. The [analysis notes](docs/model-selection-analysis.md) explain how those results inform the guide.

These are **API-priced benchmark comparisons, not subscription allowance measurements**. The cost column is a suite-wide average, not the cost of each individual evaluation. Composite scores do not establish which model will finish a particular repository task. Small score differences are not a reliable basis for a universal ranking.

The [research references](docs/agent-coordination-references.md) support careful task boundaries, verification and comparisons with simpler approaches. They do not establish that a standing team is cheaper or more accurate than one capable agent.

To evaluate the skill, compare the same tasks with a single agent, unguided delegation and skill-guided delegation. Keep starting states, acceptance checks and relevant configurations controlled. Count preparation, workers, reviews, failed attempts and integration; report acceptance rate and total spending per accepted result together. Repeat trials and test configuration changes one at a time. Measure each provider's allowance consumption separately from API estimates. These comparisons remain to be run; the skill does not yet have measured workflow savings.

## What agents load

| File | Purpose | Loaded during ordinary deployment? |
| --- | --- | --- |
| [SKILL.md](SKILL.md) | Scope, ownership, verification, continuation and waiting | When the skill is selected |
| [Model-selection guide](references/model-selection.md) | Model comparisons, relative costs, effort choices and acceptance evidence | When choosing a worker |
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
