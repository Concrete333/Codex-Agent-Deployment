# Agent Deployment for Codex

Delegate work your coordinator can stop doing—not work it will have to do again to check the answer. Use Luna, Terra, Sol or Opus 5 when a bounded assignment can reduce total cost, and keep hard, coupled reasoning with your current Codex agent.

This skill helps your current Codex agent decide **whether to delegate, which model and effort to use, and how to accept the result**. It offers starting recommendations rather than assigning every kind of work to a fixed model. A small task can stay with the coordinator; a difficult task does not automatically need a team.

[Install](#install) · [Use](#use) · [Model guide](references/model-selection.md) · [Test results](#what-weve-measured)

## How it works

Your current agent remains the coordinator. It owns the required outcome and cross-cutting decisions, chooses workers when they help, integrates changes and makes the final acceptance decision. Workers own local implementation choices within their assignments.

| Before a worker starts | While it works | Before accepting the result |
| --- | --- | --- |
| Identify work removed from the coordinator and how to check it. Then choose a worker and define ownership and done. | Keep coupled implementation, tests and fixes together. Avoid duplicate investigation and unnecessary status polling. | Check the agreed behavior and affected interactions. Finish when acceptance is supported; reopen for new evidence or required review. |

Worker choice is flexible within four families: **Luna, Terra, Sol and Opus 5**. Astra and Fable are not worker options. The coordinator cannot lower the acceptance standard to fit a budget.

**Your coordinator keeps its model and effort.** An Astra High coordinator handles difficult reasoning and final acceptance itself. It can delegate a bounded substantive review without repeating that review afterward; it does not spawn another Astra.

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

## Optional software runner

The included [deployment runner](references/software-runner.md) handles one configured CLI worker, process completion, predefined checks and saved receipts. It uses Luna, Terra or Sol through Codex, or Opus 5 through the Claude wrapper. Python owns the bookkeeping; your coordinator owns review and acceptance.

The runner prevents accidental repeats of the same request, keeps full logs out of routine model context, detects changes to declared checker files and retains ownership after interrupted work. It does not choose models, retry automatically or treat passing tests as acceptance.

This route is experimental and optional. A [host-managed adapter replication](docs/benchmarks/runner-comparison/results-host-pipeline-replication-2026-09-11.md) cost 22.9% less than one native-delegation baseline, including an acceptance-stage code repair. That comparison does not isolate waiting as the cause. Use native subagents when their event-driven completion wait is already sufficient. The [design and qualification notes](docs/software-runner-design.md) explain the runner's scope and what we borrowed from Symphony.

A one-shot host bridge also supports Codex coordinators whose sandbox cannot access CLI authentication. One live Luna Max smoke test passed with sandboxed checks; the coordinator still owns acceptance. Setup is in the [runner guide](references/software-runner.md#sandboxed-coordinator-without-cli-authentication).

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

The short entrypoint first asks whether to delegate at all. The coordinator identifies work it can hand over and how to check the result, including any necessary source rereading. If preparation, checking and likely repairs erase the benefit, it works locally without loading the operational references or model guide.

A repository search can spare the coordinator a large amount of source context. A settled component can give a worker useful ownership of implementation, tests and corrections. Splitting tightly coupled work between an implementer and a test writer may instead make both agents learn the same behavior and leave the coordinator to reconcile them. Independent test design or review is useful when it addresses a specific risk.

“Write tests” is not automatically cheap work. Extending a known fixture with agreed expected results is different from discovering which regression cases expose unfamiliar behavior. Model choice follows the uncertainty, not the type of file being written.

Choose who verifies the result before dispatch. Reuse independent checks for objective requirements; worker-written tests can supplement them, but passing a self-check is not acceptance. Exact quotations do not prove that a claim is supported. A cheaper reviewer can replace substantive coordinator review only with a basis for trusting it on the relevant errors—not merely because it reports full coverage. The coordinator retains final acceptance and inspects unresolved risks without routinely duplicating a qualified review. Required full coverage cannot be replaced with spot checks.

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

The baseline matters: if Astra's implementation needs no separate review, Luna plus acceptance costs **6.31% more**. Acceptance accounts for 90.28% of the Luna path. This clean pair cannot tell us whether the extra review is necessary or whether a cheaper reviewer would be adequate. The Astra reviewer sessions were explicit benchmark exceptions; the skill does not allow Astra workers.

### Other results worth knowing

| Test | Observed result | What passed, and the limit |
| --- | --- | --- |
| [Saved inventory implementations with fresh acceptance](docs/benchmarks/inventory-events/acceptance-results-2026-09-12.md) | $1.047 versus $0.545: 47.98% lower | Both passed 21 checks and separate reviews. Retrospective accounting on the same inventory task, not a second fresh pipeline. |
| [Six-adapter pair and repeat](docs/benchmarks/adapter-batch/results-replication-02-2026-09-10.md) | Team cost 18.4% and 10.4% less than solo | All four passed 226 frozen cases. A later large-CSV probe exposed a defect in the first pair and reference; both repeat submissions passed it. |
| [Repository search: Luna Max with/without scoped-search guidance](docs/benchmarks/context-scope/replication-results-2026-09-12.md) | Combined worker cost 24.9% lower | All four runs returned the exact required matches. Two small searches; excludes coordinator acceptance. |
| [Reservation implementation: same guidance, three pairs](docs/benchmarks/reservation-component/unattended-results-2026-09-12.md) | Effectively tied across repeats | All six accepted. Two initial savings reversed in the third pair; search guidance did not establish cheaper implementation. |
| [Earlier cattrs feature](docs/benchmarks/cattrs-self/results-2026-09-10.md) | Solo $1.44; unguided team $2.45; skill team at least $3.02 | Saved code passed the checks, but the skill run timed out. Its worker cost only $0.05; coordinator work dominated. |

These are historical API-equivalent estimates, **not subscription bills or quota savings**. Execution comparisons exclude shared research preparation and later adjudication. For the latest pipeline, the four sessions together cost $1.417; adding measured setup and a partial adjudication record brought research spending to at least $4.005. Full accounting is in each report.

The successful team comparisons fixed the worker assignment. They do not show that the skill reliably chooses when to delegate. Trials are small, often one run per condition, with uncontrolled cache/order effects. Lower dollar cost can also mean more tokens: the latest Luna implementation used about seven times Astra's input tokens.

### What this means for your work

Give a worker a settled component it can own through tests and bounded corrections. Keep shared integration files with one writer, and use completion notifications instead of status polling. Retain the review your task needs; our tests do not justify removing it simply to improve the cost result.

In a [real catalogue implementation](docs/ccu-target-selection-delegation-audit-2026-09-12.md), Luna handled target selection and several review corrections for about $0.50. The integrated application ran 2,567 tests with one skipped. There was no solo comparison, and the parent handled substantial other work, so we make no savings claim for that run.

The [test handoff](docs/claude-orchestration-findings-2026-09-12.md) collects methods, failures and follow-up questions. The [combined model evidence](docs/model-performance-comparison.md) covers 38 GPT/Claude configurations from the 8 September 2026 Artificial Analysis capture; [analysis notes](docs/model-selection-analysis.md) and [coordination research](docs/agent-coordination-references.md) explain the reasoning behind the guidance. Suite averages help choose candidates; they cannot price your task or establish reviewer reliability.

## What agents load

| File | Purpose | Loaded during ordinary deployment? |
| --- | --- | --- |
| [SKILL.md](SKILL.md) | Local-or-delegate decision, worker boundaries and reference routing | When the skill is selected |
| [Delegation guide](references/delegation.md) | Ownership, verification, continuation and waiting | Only when delegation is useful |
| [Model-selection guide](references/model-selection.md) | Model comparisons, relative costs and effort choices | When delegation is useful and the worker model or effort still needs choosing |
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
