# Agent Deployment

A Codex skill for choosing workers, bounding their assignments, and avoiding expensive coordinator polling.

```text
Bounded context gathering or repetitive work -> Luna Max
Uncertain cause or design -> Sol High
Difficult, specified implementation -> Astra Low
One unsuccessful Luna assignment or Sol diagnosis -> Astra Low
Consequential work -> optional independent Sol High review
```

Every Luna dispatch uses `gpt-5.6-luna` at `max`. Earlier Luna High or X-High preferences are stale. Terra is excluded from this policy.

## Why these defaults

OpenAI describes Luna as designed for cost-sensitive, high-volume workloads, Sol as a flagship for complex professional work, and Astra as its most capable model for complex reasoning and coding. These descriptions support the broad roles; they do not establish that this exact model-and-effort combination is optimal.

Luna Max, Sol High, and Astra Low are deliberate workflow defaults. A large context window does not prove equal reasoning ability, and maximum effort does not guarantee correctness. Compare completed-task usage, time, corrections, and missed defects before claiming savings. API prices and Codex allowance measurements are different evidence.

- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)

## Routing

| Work | Model and effort | Expected result |
| --- | --- | --- |
| Search substantial context or map a repository | Luna Max | Exact evidence, coverage, and unresolved questions |
| Apply repetitive changes with objective checks | Luna Max | Scoped changes and verification |
| Determine an uncertain cause or design | Sol High | Evidence-backed diagnosis and implementation contract |
| Implement difficult, settled behavior | Astra Low | Correct implementation and appropriate checks |
| Take over one unsuccessful Luna assignment or Sol diagnosis | Astra Low | Continue from evidence, resolve uncertainty, then complete the authorized work |
| Independently review consequential work | Sol High, optional | Concrete defects supported by source and verification evidence |

Repository size alone does not decide ownership. A subtle concurrency bug in a large repository belongs with Sol for diagnosis; Luna can gather bounded evidence if that helps. Skip exploration when the coordinator already has adequate evidence. Small tasks usually stay local.

Sol's diagnosis should include discriminating checks, remaining uncertainty, and a proposed contract. It does not include production implementation; explicitly assign any scratch/test edits needed for reproduction. Review is read-only, with corrections routed to the appropriate implementation owner and focused rechecks as needed. Use a fresh reviewer when independence from the original diagnosis or design matters.

## What counts as failure?

One substantive failure of a **bounded Luna assignment or Sol diagnosis** triggers escalation. An ordinary failing test during implementation, including a regression test written before the fix, does not. Trivial Luna corrections can stay local.

Allow reasonable local correction within an agreed work budget. Stop and report when the same approach fails again without new evidence or a hard budget is exhausted. At a checkpoint, useful progress can justify a revised estimate within user limits; lateness alone is not model failure. Report unresolved acceptance failures, incorrect assumptions, missing requirements, and useful partial work.

Substantive non-trivial Luna failures and substantive Sol diagnosis failures go directly to Astra Low. Transient tool failures and external blockers do not prove model failure. A reviewer finding defects has succeeded. If Astra also fails, inspect the cause before changing effort or adding workers. The coordinator owns these decisions; workers do not redelegate unless explicitly assigned that authority.

## Waiting and worker health

Use native event waits while workers run and no useful independent coordinator work remains. Prefer completion and blocker signals over timed status checks.

When supported **and permitted by higher-priority instructions**, 25 minutes (`1500000` ms) is a practical default. Adjust for checkpoints and deadlines; longer waits can be appropriate. If the runtime or responsiveness instructions require shorter waits, use the longest appropriate permitted interval without adding status reads or interruptions after each timeout.

An empty timeout proves neither failure nor health. Re-enter the wait unless a blocker, due checkpoint, or exhausted budget requires action. Never wake solely to preserve cache: OpenAI documents at least 30 minutes of cache eligibility, potentially longer, but this does not establish Codex allowance behavior or an optimal waiting interval. [Official caching documentation](https://developers.openai.com/api/docs/guides/prompt-caching)

For substantial assignments, set a rough duration estimate and a meaningful checkpoint or work budget. Workers report blockers promptly and send a compact checkpoint update when able; do not interrupt a blocking tool merely to send one. No periodic "still running" messages are needed.

If a checkpoint arrives without a useful signal, make one compact, non-interrupting check if supported. Use milestone evidence, active operations, and the agreed budget to decide whether to continue, narrow the work, or stop it. A running flag alone is not proof of progress. Scheduled automations are not part of this waiting policy.

## Safe assignments and handoffs

```text
Outcome and scope:
Owned files; read/write permissions; dependencies and interfaces:
Context entry points and search targets:
Constraints and behavior to preserve:
Acceptance checks and commands:
Expected duration; checkpoint or bounded work budget; blocker reporting:
Return: evidence or changed files, check results, unresolved risks.
```

Use minimal inherited history for new workers, and reuse suitable workers for in-scope continuations. Preserve relevant instructions and authorization explicitly. Keep handoffs concise, but retain exact failures and decision-critical evidence; link longer artifacts. Sol and Astra should read relevant source directly when deciding correctness.

Before a replacement writes to the same files, confirm the previous worker and its writing commands have stopped. Preserve partial changes and unrelated user edits, then transfer ownership with the current diff, evidence, checks, and unresolved questions. Never run competing writers during escalation.

## Installation

macOS or Linux:

```bash
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git ~/.codex/skills/agent-deployment
```

Windows PowerShell:

```powershell
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git "$env:USERPROFILE\.codex\skills\agent-deployment"
```

## Usage

```text
$agent-deployment Route this authorized delegated task: Luna Max for bounded evidence or repetitive work, Sol High for uncertain diagnosis, and Astra Low for difficult implementation or escalation. Use checkpoints and event waits without busy polling.
```

The skill does not authorize delegation, override higher-priority instructions or new explicit user choices, or guarantee savings. Runtime model and effort availability must be checked before dispatch.

`SKILL.md` contains the complete policy; `agents/openai.yaml` contains the Codex display metadata. The skill is self-contained.

## Sources and acknowledgements

Reddit user [`u/emir_morris`](https://www.reddit.com/user/emir_morris/) proposed the four-tier model ladder and practical model summaries in ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/). That post started this project.

Reddit user [`u/Icy_Piece6643`](https://www.reddit.com/user/Icy_Piece6643/) drew attention to Astra's delegation and prompting behavior in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/). The current policy is an independent adaptation built around context cost, bounded handoffs, and early escalation. It also follows [OpenAI's official Astra guidance](https://developers.openai.com/api/docs/guides/latest-model).

GitHub user [`tagorr`](https://github.com/tagorr) documented 47 empty 30-second `wait_agent` polls that caused 7.13 million Astra parent input tokens in [OpenAI Codex issue #35259](https://github.com/openai/codex/issues/35259#issuecomment-5577073962). Our own saved Codex rollouts showed the same mechanism with different intervals and percentages, motivating the rule against avoidable status polling.
