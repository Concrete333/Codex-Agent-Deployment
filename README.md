# Agent Deployment for Codex

Reduce unnecessary Codex usage while waiting for commands or coordinating other agents. This skill covers long-running commands as well as work handed to other AI agents. **You do not need subagents to use it.**

If Codex starts a slow test suite, build or database script, it can keep calling tools to ask whether the job has finished. Each model turn adds overhead. The skill guides Codex to use a completion notification, let the command run, and check its saved result when it finishes.

For larger tasks, it also helps Codex decide whether another agent would save work. It keeps assignments bounded, avoids overlapping investigation, and batches reviews after completed work. Delegation is optional; checking and correcting a worker can cost more than doing the task directly.

[Install](#install) · [Use](#use) · [Scripts and test suites](#scripts-and-test-suites) · [Agent delegation](#agent-delegation) · [Choosing models](#choosing-models) · [Test results](#what-weve-measured)

## What it changes

| When Codex is… | The skill guides it to… |
| --- | --- |
| Waiting for tests, a build, a script or a database job | Use supported completion notifications instead of repeatedly checking unchanged logs. |
| Considering another AI agent | Identify work it can actually hand over and how to verify the result. Keep small or tightly coupled work with one owner. |
| Waiting for a worker | Leave unfinished edits alone, do independent useful work, and review completed handoffs or agreed checkpoints. |
| Receiving a result | Check saved evidence before continuing. A notification or a worker saying “done” does not establish success. |

Short commands need no background setup. For longer work, the skill prefers an existing native completion mechanism. Its bundled helper can save the command's result and send Codex one follow-up message when supported. If neither route is available, Codex explains what is running and asks you to check back.

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

For a plan only:

```text
$agent-deployment Plan this migration. Include models, efforts, ownership
and acceptance checks. Do not start workers or edit files.
```

Codex can select the skill when a request matches its description. Explicitly naming it is the clearest way to request it. Skill selection does not itself authorize delegation, edits or additional spending.

### Optional reminder in AGENTS.md

Where you don't want to manually name the skill in every new chat, add this paragraph to your existing project or global `AGENTS.md` after installing it. It is the routing reminder used in this project's local setup:

```text
Before launching an expected long-running job, including a test suite, use the
`agent-deployment` skill's waiting guide to establish native completion or preflight
and arm its queue helper. Known-short commands stay direct, even full suites; use
existing timing evidence, not a separate timing run. This applies without subagents.
Do not launch first and default to manual check-in later; if notification is
unavailable, state the specific limitation.
```

You can use the skill without editing `AGENTS.md`, the detailed waiting and recovery rules are already in the skill; this reminder makes the pre-launch instruction available during ordinary coding tasks. As with everything Codex, this still won't guarantee skill selection, instruction compliance or notification delivery, but it lines it up as well as we can.

## Scripts and test suites

The same waiting guidance applies to builds, data-processing scripts and database jobs. No additional AI worker is needed.

Where supported, Codex can start a command that safely continues in the background, end its turn, and receive one queued message after the helper saves the result. The same mechanism works for a foreground worker CLI. The optional `AGENTS.md` reminder above helps Codex choose this route before launch.

The [waiting guide](references/waiting.md) covers setup, saved execution records and recovery. Script-only tasks skip the model-selection guides. The command must have appropriate timeout and cleanup controls; a notification is not proof of success. If the host cannot deliver notifications, Codex tells you to check back rather than repeatedly polling. Already-running jobs are not restarted just to add notification.

## Agent delegation

Your current Codex agent is the coordinator: it defines the outcome, owns consequential decisions and checks the final result. A worker is another AI agent given a bounded assignment, such as implementing a component with settled interfaces or searching specified source files.

Before dispatch, Codex considers preparation, worker execution, review and likely corrections. It should hand over work it can stop doing itself. The worker owns implementation and tests within its assignment; the coordinator reviews completed work and sends corrections together instead of repeatedly inspecting partial edits.

The core guidance has no model allowlist. Your current agent keeps its model and effort unless you ask to change them, and worker choices respect your available tools and preferences. Required verification stays in place even when a cheaper worker is used.

## Choosing models

The optional [model-selection guide](references/model-selection.md) explains suggested task fits and efforts, all based on current AI benchmarking. Codex skips it when you have already chosen a model. Unlisted models can also be used through supported, authorized tools.

A few starting points:

| Work | Starting candidate |
| --- | --- |
| Bounded extraction, source mapping or pattern-following edits with objective checks | Luna Max |
| Bounded native implementation with settled interfaces and regression checks | Terra Max |
| Supplied analytical or scientific subproblem | Sol Low/Medium |
| Bounded diagnosis, analysis or independently justified review | Sol High |
| Bounded implementation through an authorized Claude subscription | Opus 5 Low |
| Open-ended diagnosis, architecture, difficult coupled work and final judgment | Current Codex agent; no worker |

These are starting recommendations, not a required sequence or effort restriction. Choose a different model or effort when your preferences or task evidence support it. Include checking and corrections when comparing cost.

Choose Luna when the job mostly finds evidence or follows a fixed pattern. Choose Terra when implementation needs more local judgment. Sol fits supplied problems requiring derivation or evaluation. Opus 5 offers a Claude implementation route when its account access, retained context or task results justify the setup.

For scale, captured suite-average costs are $0.18 for Luna Max, $0.50 for Sol Medium, $1.10 for Opus 5 Low and $1.40 for Terra Max. These are not prices for your particular assignment. Compare the worker, preparation and review together against keeping the work local; lowering effort does not itself lower a model's per-token price.

“Accepted” means the requested outcome is supported by appropriate evidence: reconciled source coverage for extraction, a discriminating reproduction for diagnosis, or behavior and integration checks for implementation. A worker reporting completion is not enough.

The goal is lower total cost while meeting the required correctness standard, not faster completion. The choice depends on uncertainty, available checks, the consequences of a missed defect, context already held by a worker and your authorized account preferences. Commands and scripts come first for exact work that does not need another model.

Claude is optional. Using two providers is not a goal in itself, and a provider switch does not automatically improve a result.

## Optional software runner

The included [deployment runner](references/software-runner.md) handles one configured CLI worker, process completion, predefined checks and saved execution records. It uses Luna, Terra or Sol through Codex, or Opus 5 through the Claude wrapper. Python owns the bookkeeping; your coordinator owns review and acceptance.

The runner prevents accidental repeats of the same request, keeps full logs out of routine model context, detects changes to declared checker files and retains ownership after interrupted work. It does not choose models, retry automatically or treat passing tests as acceptance.

This route is experimental and optional. A [host-managed adapter replication](docs/benchmarks/runner-comparison/results-host-pipeline-replication-2026-09-11.md) cost 22.9% less than one native-delegation baseline, including an acceptance-stage code repair. That comparison does not isolate waiting as the cause. Use native subagents when their event-driven completion wait is already sufficient. The [design and qualification notes](docs/software-runner-design.md) explain the runner's scope and its use of OpenAI's Symphony orchestration project as a design reference.

A one-shot host bridge also supports Codex coordinators whose sandbox cannot access CLI authentication. One live Luna Max smoke test passed with sandboxed checks; the coordinator still owns acceptance. Setup is in the [runner guide](references/software-runner.md#sandboxed-coordinator-without-cli-authentication).

## Claude CLI workers

Codex calls your installed Claude Code CLI through the included Python wrapper; no MCP server required. The wrapper accepts only Opus 5, with explicit effort, read-only or editing profiles, session resumption and bounded batches of independent workers.

Requirements: Python 3.10+, Claude Code 2.1.108+ and a logged-in Claude subscription with access to the selected model. The wrapper supports `low`, `medium`, `high`, `xhigh` and `max`; the selected model and installed CLI must support the requested setting.

Workers use five-minute caching and disabled skill discovery while retaining Claude's default coding prompt. The wrapper requests no automatic model fallback or API billing fallback. Compact results link to complete local execution records.

See [the Claude CLI guide](references/claude-cli.md) for setup, request format, permission profiles and continuation.

Important limits:

- Tool restrictions are not an operating-system sandbox. The target repository and inherited Claude context must be trusted.
- Usage records contain estimates, not remaining subscription allowance. The wrapper cannot disable account-side paid overflow.
- A successful CLI exit is not accepted work. The coordinator still checks results, artifacts and unresolved risks.
- Concurrent editing jobs need separate checkouts and independent shared state. A worker timeout terminates work; a coordinator wait timeout does not.

## Where the savings should come from

For script-only work, the skill loads just the waiting guide. Waiting moves into software where supported, avoiding repeated model turns to inspect unchanged status.

For agent work, the skill first asks whether to delegate at all. The coordinator identifies work it can hand over and how to check the result, including any necessary source rereading. If preparation, checking and likely repairs erase the benefit, it works locally without loading the operational references or model guide.

A repository search can spare the coordinator a large amount of source context. A settled component can give a worker useful ownership of implementation, tests and corrections. Splitting tightly coupled work between an implementer and a test writer may instead make both agents learn the same behavior and leave the coordinator to reconcile them. Independent test design or review is useful when it addresses a specific risk.

“Write tests” is not automatically cheap work. Extending an existing test setup with agreed expected results is different from discovering which regression cases expose unfamiliar behavior. Model choice follows the uncertainty, not the type of file being written.

Choose who verifies the result before dispatch. Reuse independent checks for objective requirements; worker-written tests can supplement them, but passing a self-check is not acceptance. Exact quotations do not prove that a claim is supported. A cheaper reviewer can replace substantive coordinator review only with a basis for trusting it on the relevant errors, not merely because it reports full coverage. The coordinator retains final acceptance and inspects unresolved risks without routinely duplicating a qualified review. Required full coverage cannot be replaced with spot checks.

Workers receive focused assignments and return concise evidence, not their entire investigation. The coordinator does not duplicate active worker work. It uses supported completion waits instead of repeated status checks; if suitable waiting is unavailable, it keeps the work local or reports the limitation.

Mechanical errors and bounded defects within a sound approach can go back to the worker. A failed core approach or newly exposed design work returns to the coordinator; do not repeat that failed assignment on Luna. There is no mandatory model ladder.

## What we've measured

A cheap worker helps only if its handoff, review and repairs cost less than the work it replaces. We test that with frozen tasks, saved usage and independent checks.

Our latest inventory test gave Luna Max a complete component to implement, then used a separate Astra High session for acceptance. Software handled the transitions, so no coordinating model sat waiting between stages.

| Inventory pipeline | Implementation | Read-only acceptance | Total |
| --- | ---: | ---: | ---: |
| Astra High implementation + Astra High acceptance | $0.560 | $0.263 | $0.822 |
| Luna Max implementation + Astra High acceptance | $0.058 | $0.537 | $0.595 |

**27.65% lower execution cost with the same separate-review requirement.** Both implementations passed all 21 public/independent test methods and their added tests. Both reviews accepted without findings, edits or a correction round. Totals use unrounded values. [Full results and protocol](docs/benchmarks/inventory-events/pipeline-results-2026-09-12.md).

The baseline matters: if Astra's implementation needs no separate review, Luna plus acceptance costs **6.31% more**. Acceptance accounts for 90.28% of the Luna path. This clean pair cannot tell us whether the extra review is necessary or whether a cheaper reviewer would be adequate. The comparison explicitly selected Astra for review; it does not require that model for everyday use.

### Other results worth knowing

| Test | Observed result | What passed, and the limit |
| --- | --- | --- |
| [Saved inventory implementations with fresh acceptance](docs/benchmarks/inventory-events/acceptance-results-2026-09-12.md) | $1.047 versus $0.545: 47.98% lower | Both passed 21 checks and separate reviews. Retrospective accounting on the same inventory task, not a second fresh pipeline. |
| [Six-adapter pair and repeat](docs/benchmarks/adapter-batch/results-replication-02-2026-09-10.md) | Team cost 18.4% and 10.4% less than solo | All four passed 226 frozen cases. A later large-CSV probe exposed a defect in the first pair and reference; both repeat submissions passed it. |
| [Repository search: Luna Max with/without scoped-search guidance](docs/benchmarks/context-scope/replication-results-2026-09-12.md) | Combined worker cost 24.9% lower | All four runs returned the exact required matches. Two small searches; excludes coordinator acceptance. |
| [Reservation implementation: same guidance, three pairs](docs/benchmarks/reservation-component/unattended-results-2026-09-12.md) | Effectively tied across repeats | All six accepted. Two initial savings reversed in the third pair; search guidance did not establish cheaper implementation. |
| [Earlier cattrs feature](docs/benchmarks/cattrs-self/results-2026-09-10.md) | Solo $1.44; unguided team $2.45; skill team at least $3.02 | Saved code passed the checks, but the skill run timed out. Its worker cost only $0.05; coordinator work dominated. |

These are historical API-equivalent estimates, **not subscription bills or quota savings**. Execution comparisons exclude shared research preparation and later analysis of disputed results. For the latest pipeline, the four sessions together cost $1.417; adding measured setup and a partial record of that analysis brought research spending to at least $4.005. Full accounting is in each report.

The successful team comparisons fixed the worker assignment. They do not show that the skill reliably chooses when to delegate. Trials are small, often one run per condition, with uncontrolled cache/order effects. Lower dollar cost can also mean more tokens: the latest Luna implementation used about seven times Astra's input tokens.

### What this means for your work

Give a worker a settled component it can own through tests and bounded corrections. Keep shared integration files with one writer, and use completion notifications instead of status polling. Retain the review your task needs; our tests do not justify removing it simply to improve the cost result.

In a [real catalogue implementation](docs/ccu-target-selection-delegation-audit-2026-09-12.md), Luna handled target selection and several review corrections for about $0.50. The integrated application ran 2,567 tests with one skipped. There was no solo comparison, and the parent handled substantial other work, so we make no savings claim for that run.

The [test summary](docs/claude-orchestration-findings-2026-09-12.md) collects methods, failures and follow-up questions. The [combined model evidence](docs/model-performance-comparison.md) covers 38 GPT/Claude configurations from the 8 September 2026 Artificial Analysis capture; [analysis notes](docs/model-selection-analysis.md) and [coordination research](docs/agent-coordination-references.md) explain the reasoning behind the guidance. Suite averages help choose candidates; they cannot price your task or establish reviewer reliability.

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

## Credits

I got the initial idea from these posts and implemented their model-routing and delegation ideas in this skill. Neither post is mine:

- [u/emir_morris: GPT-6 Astra: Everything You Need to Know](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/).
- [u/Icy_Piece6643: Before blaming GPT-6 Astra, read its prompting guide](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/).

Further work drew on [tagorr's polling telemetry](https://github.com/openai/codex/issues/35259#issuecomment-5577073962), [u/PilgrimofHaqq2's parallel/sequential research discussion](https://www.reddit.com/r/claude/comments/1w7k9au/parallel_vs_sequential_agent_systems_research/), and the primary sources in the [reference list](docs/agent-coordination-references.md).

Model evidence comes from [Artificial Analysis](https://artificialanalysis.ai/models), with vendor context from [OpenAI](https://developers.openai.com/api/docs/guides/latest-model) and [Anthropic](https://platform.claude.com/docs/en/models/fable-5-1/overview). The deployment recommendations are this project's interpretation, to be tested against real accepted outcomes.
