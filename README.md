# Agent Deployment for Codex

Reduce unnecessary Codex usage while waiting for commands or coordinating other agents. **You do not need subagents to use it.**

If Codex starts a slow test suite, build or database script, it can keep calling tools to ask whether the job has finished. Each model turn adds overhead. The skill guides Codex to use a completion notification, let the command run, and check its saved result when it finishes.

For larger tasks, it helps Codex hand over bounded work and review completed results without duplicating the worker's investigation. Delegation is optional: checking and correcting a worker can cost more than doing the task yourself.

[Install](#install) · [Use](#use) · [Scripts and test suites](#scripts-and-test-suites) · [Agent delegation](#agent-delegation) · [Choosing models](#choosing-models) · [Test results](#what-weve-measured)

## What it changes

| When Codex is… | The skill guides it to… |
| --- | --- |
| Waiting for tests, a build, a script or a database job | Use supported completion notifications instead of repeatedly checking unchanged logs. |
| Considering another AI agent | Identify work it can actually hand over and how to verify the result. Keep small or tightly coupled work with one owner. |
| Waiting for a worker | Leave unfinished edits alone, do independent useful work, and review completed handoffs or agreed checkpoints. |
| Receiving a result | Check saved evidence before continuing. A notification or a worker saying “done” does not establish success. |

Short commands stay direct. Longer work uses native completion or the bundled notification helper where supported. If neither is available, Codex explains what is running and asks you to check back.

## Install

Use Git to clone the skill. The bundled completion helper needs Python 3.10+ and a native Codex CLI supporting `codex queue`. Subagents are optional; choosing their models and reasoning efforts requires a Codex environment that exposes those controls. The skill does not unlock models or change account access.

For a new user-level installation, use the skills location in [OpenAI's documentation](https://learn.chatgpt.com/docs/build-skills).

macOS or Linux:

```bash
git clone https://github.com/Concrete333/Codex-Delegation-Deployment.git ~/.agents/skills/agent-deployment
```

Windows PowerShell:

```powershell
git clone https://github.com/Concrete333/Codex-Delegation-Deployment.git "$env:USERPROFILE\.agents\skills\agent-deployment"
```

If Codex already discovers an installation elsewhere, update that copy instead of creating a duplicate. Restart Codex if the skill does not appear.

## Use

For a long-running command:

```text
$agent-deployment Run the full test suite. Use completion notification
instead of repeated status checks, preserve safety timeouts, and verify
the results before continuing. No subagents are needed.
```

For a task where delegation may help:

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

Codex can select the skill when a request matches its description. Explicitly naming it is the clearest way to request it. Skill selection does not itself authorize delegation, edits or additional spending.

### Optional reminder in AGENTS.md

To make the pre-launch reminder available in ordinary coding tasks, add this paragraph to your project or global `AGENTS.md` after installing the skill:

```text
Before launching an expected long-running job, including a test suite, use the
`agent-deployment` skill's waiting guide to establish native completion or preflight
and arm its queue helper. Known-short commands stay direct, even full suites; use
existing timing evidence, not a separate timing run. This applies without subagents.
Do not launch first and default to manual check-in later; if notification is
unavailable, state the specific limitation.
```

The skill contains the full waiting and recovery rules; this reminder helps Codex select them before launch. Neither file guarantees instruction compliance or notification delivery.

## Scripts and test suites

Codex can launch a command that safely continues in the background, end its turn, and receive one queued message after the helper saves the terminal result. This works for tests, builds, data-processing jobs and external worker CLIs where the host supports it.

The [waiting guide](references/waiting.md) covers setup and recovery. Commands retain safety timeouts and cleanup controls. Codex verifies saved results before continuing; a notification alone does not establish success. Already-running jobs are not restarted just to add notifications. Script-only tasks skip the delegation and model-selection guides.

### Optional native-agent wait configuration

To prevent short timeout loops when waiting for native subagents, add or merge this into your Codex `config.toml`:

```toml
[features.multi_agent_v2]
enabled = true
min_wait_timeout_ms = 1500000
default_wait_timeout_ms = 1500000
max_wait_timeout_ms = 1500000
```

The timeout is 25 minutes; supported completion events can end the wait sooner. In our [CLI 0.153.4 probe](docs/benchmarks/waiting/README.md), one wait returned after 50.13 seconds when the worker finished, without parent polling. That verifies early completion in the tested runtime, not savings against default settings or compatibility with future versions. Respect your host's wait limits.

Use native waiting for subagents when it works. Use the queue helper for suitable background commands or external workers without an equivalent completion route.

## Agent delegation

Your current Codex agent is the coordinator: it defines the outcome, owns consequential decisions and checks the final result. A worker is another AI agent given a bounded assignment, such as implementing a component with settled interfaces or searching specified source files.

Before dispatch, Codex considers preparation, worker execution, review and likely corrections. The worker should remove work from the coordinator, owning implementation and tests within settled boundaries. The coordinator leaves partial edits alone and batches corrections after completed handoffs or agreed checkpoints.

Keep shared integration files with one writer. Review evidence against the task's requirements; passing worker-written tests alone is insufficient. Bounded defects can go back to the worker, while failed approaches and newly exposed design decisions return to the coordinator. Small or tightly coupled work often costs less to finish locally.

The core guidance has no model allowlist. Your current agent keeps its model and effort unless you ask to change them, and worker choices respect your available tools and preferences. Required verification stays in place even when a cheaper worker is used.


## Choosing models

The optional [model-selection guide](references/model-selection.md) explains task fits and efforts using captured benchmarks and local task results. Codex skips it when you have already chosen the worker model and effort. Unlisted models can also be used through supported, authorized tools.

A few starting points:

| Work | Starting candidate |
| --- | --- |
| Bounded extraction, source mapping or pattern-following edits with objective checks | Luna Max |
| Bounded native implementation with settled interfaces and regression checks | Terra Max |
| Supplied analytical or scientific subproblem | Sol Low/Medium |
| Bounded diagnosis, analysis or independently justified review | Sol High |
| Bounded implementation through an authorized Claude subscription | Opus 5 Low |
| Open-ended diagnosis, architecture, difficult coupled work and final judgment | Current Codex agent; no worker |

These are starting candidates, not a required sequence. Choose for the uncertainty remaining, available checks and consequences of a missed defect. The guide explains relative costs and alternatives; benchmark averages cannot price your assignment or establish reviewer reliability.

Compare the complete accepted result, including preparation and corrections, against local completion. Lower effort does not itself lower per-token prices. Use commands and scripts for exact work that needs no additional model, and keep provider changes optional.

## Optional software runner

The included [deployment runner](references/software-runner.md) handles one configured CLI worker, process completion, predefined checks and saved execution records. It uses Luna, Terra or Sol through Codex, or Opus 5 through the Claude wrapper. Python owns the bookkeeping; your coordinator owns review and acceptance.

The runner prevents accidental repeats of the same request, keeps full logs out of routine model context, detects changes to declared checker files and retains ownership after interrupted work. It does not choose models, retry automatically or treat passing tests as acceptance.

This route is experimental and optional. Use native subagents when their completion wait is sufficient. The [runner guide](references/software-runner.md#sandboxed-coordinator-without-cli-authentication) also covers coordinators whose sandbox cannot access CLI authentication. See the [design notes](docs/software-runner-design.md) for scope and qualification, including the use of OpenAI's Symphony as a design reference.

## Claude CLI workers

Codex calls your installed Claude Code CLI through the included Python wrapper; no MCP server required. The wrapper accepts only Opus 5, with explicit effort, read-only or editing profiles, session resumption and bounded batches of independent workers.

Requirements: Python 3.10+, Claude Code 2.1.108+ and a logged-in Claude subscription with access to the selected model. The wrapper supports `low`, `medium`, `high`, `xhigh` and `max`; the selected model and installed CLI must support the requested setting.

See [the Claude CLI guide](references/claude-cli.md) for setup, context controls, request format and session continuation. Compact results link to complete local execution records.

Important limits:

- Tool restrictions are not an operating-system sandbox. The target repository and inherited Claude context must be trusted.
- Usage records contain estimates, not remaining subscription allowance. The wrapper cannot disable account-side paid overflow.
- A successful CLI exit is not accepted work. The coordinator still checks results, artifacts and unresolved risks.
- Concurrent editing jobs need separate checkouts and independent shared state. A worker timeout terminates work; a coordinator wait timeout does not.

## What agents load

| File | Purpose | Loaded during ordinary deployment? |
| --- | --- | --- |
| [SKILL.md](SKILL.md) | Routes command-only tasks to waiting guidance; helps decide whether to delegate other work | When the skill is selected |
| [Waiting guide](references/waiting.md) | Completion notifications, saved results and recovery for commands and workers | For long-running work needing a completion route |
| [Delegation guide](references/delegation.md) | Ownership, verification, continuation and waiting | Only when delegation is useful |
| [Model-selection guide](references/model-selection.md) | Model comparisons, relative costs and effort choices | When delegation is useful and the worker model or effort still needs choosing |
| [Claude CLI guide](references/claude-cli.md) | How to invoke and manage Claude workers | For Claude delegation only |
| [Combined evidence](docs/model-performance-comparison.md), [analysis](docs/model-selection-analysis.md), workbooks and [research](docs/agent-coordination-references.md) | Audits and skill improvement | No |

Workers receive their assignment and relevant project evidence, not the entire routing guide or benchmark collection. Audits and maintenance may read the relevant material in `docs/`.

For a Claude Code coordinator instead of Codex, see [Claude Agent Deployment](https://github.com/Concrete333/Claude-Agent-Deployment).

## What we've measured

A cheap worker helps only if its handoff, review and repairs cost less than the work it replaces. We test that with frozen tasks, saved usage and independent checks.

### Comparison Test: Astra alone versus Astra + Luna

On 22 September 2026, each route received the same inventory-component implementation task in a fresh checkout. The solo baseline used one Astra High session with no added reviewer. The delegated route used Luna Max for implementation, followed by Astra High for acceptance. Software supplied the brief and handled completion, so no model spent turns waiting or rewriting the assignment.

| Route | Implementation | Astra acceptance | Total | Independent checks |
| --- | ---: | ---: | ---: | --- |
| Astra High alone | $0.756 | Included | **$0.756** | 27/27 methods |
| Luna Max + Astra High | $0.042 | $0.641 | **$0.683** | 27/27 methods |

**The delegated route cost 9.7% less, saving about $0.073.** Luna passed all independent checks before review. Astra added six acceptance tests and made no changes to Luna's implementation. Acceptance accounted for 94% of the delegated cost, so this result does not justify skipping review or assuming a cheaper reviewer would preserve accuracy.

The checks included an 80-scenario lifecycle matrix within one test method. Before the runs, the grader passed the correct controls and rejected the starter and nine defective variants. Passing this suite is evidence for the tested behavior, not proof of defect-free code. [Full results and protocol](docs/benchmarks/inventory-events/three-arm-results-2026-09-22.md).

*The same comparison included MiMo (the newest "most efficient" model as of this writing, routed through Kilo Code). It failed with a provider/runtime stream error before producing edits, tests or a handoff. Astra then implemented the task itself. Captured cost was **at least $0.877**, with failed-request usage unknown. This route did not save money in that run; the evidence cannot isolate Kilo from the provider or judge MiMo's coding ability.

### Other results worth knowing

| Test | Observed result | What passed, and the limit |
| --- | --- | --- |
| [Earlier inventory pair with separate reviews for both](docs/benchmarks/inventory-events/pipeline-results-2026-09-12.md) | Astra + Astra $0.822; Luna + Astra $0.595: 27.65% lower | Both passed 21 methods. Without the extra Astra-only review, delegation cost 6.31% more. Different protocol from the fresh solo comparison above. |
| [Six-adapter pair and repeat](docs/benchmarks/adapter-batch/results-replication-02-2026-09-10.md) | Team cost 18.4% and 10.4% less than solo | All four passed 226 frozen cases. A later large-CSV probe exposed a defect in the first pair and reference; both repeat submissions passed it. |
| [Repository search: Luna Max with/without scoped-search guidance](docs/benchmarks/context-scope/replication-results-2026-09-12.md) | Combined worker cost 24.9% lower | All four runs returned the exact required matches. Two small searches; excludes coordinator acceptance. |
| [Reservation implementation: same guidance, three pairs](docs/benchmarks/reservation-component/unattended-results-2026-09-12.md) | Effectively tied across repeats | All six accepted. Two initial savings reversed in the third pair; search guidance did not establish cheaper implementation. |
| [Earlier cattrs feature](docs/benchmarks/cattrs-self/results-2026-09-10.md) | Solo $1.44; unguided team $2.45; skill team at least $3.02 | Saved code passed the checks, but the skill run timed out. Its worker cost only $0.05; coordinator work dominated. |

These are API-equivalent estimates and, for Kilo, reported costs, **not subscription bills or quota savings**. Totals use unrounded values and exclude shared research setup, supervision and later analysis. The latest comparison has one run per route. Earlier trials are also small, with cache and run-order effects that limit generalization.

The successful implementation comparisons fixed the worker assignment. They do not show that the skill chooses when to delegate better than an unguided agent. The latest Luna route also used more raw tokens than solo despite its lower estimated cost.

Further evidence: [earlier test summary](docs/claude-orchestration-findings-2026-09-12.md), [model comparisons](docs/model-performance-comparison.md), [selection analysis](docs/model-selection-analysis.md) and [coordination research](docs/agent-coordination-references.md). Benchmark captures are dated; use comparable accepted task results to evaluate your own setup.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) to improve or audit the skill. Runtime instructions live in `SKILL.md` and `references/`; contributor guidance and research stay outside ordinary skill use. The repository's `AGENTS.md` is for working on this repository, not a file to copy into your project. Use the [optional reminder](#optional-reminder-in-agentsmd) above instead.

## Credits

I got the initial idea from these posts and implemented their model-routing and delegation ideas in this skill. Neither post is mine:

- [u/emir_morris: GPT-6 Astra: Everything You Need to Know](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/).
- [u/Icy_Piece6643: Before blaming GPT-6 Astra, read its prompting guide](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/).

Further work drew on [tagorr's polling telemetry](https://github.com/openai/codex/issues/35259#issuecomment-5577073962), [u/PilgrimofHaqq2's parallel/sequential research discussion](https://www.reddit.com/r/claude/comments/1w7k9au/parallel_vs_sequential_agent_systems_research/), and the primary sources in the [reference list](docs/agent-coordination-references.md).

The post [I investigated why GPT-6 Astra burns quota so fast](https://www.reddit.com/r/codex/comments/1wa9c9d/i_investigated_why_gpt6_astra_burns_quota_so_fast/) informed the native-agent wait configuration documented above.

Model evidence comes from [Artificial Analysis](https://artificialanalysis.ai/models), with vendor context from [OpenAI](https://developers.openai.com/api/docs/guides/latest-model) and [Anthropic](https://platform.claude.com/docs/en/models/fable-5-1/overview). The deployment recommendations are this project's interpretation, to be tested against real accepted outcomes.
