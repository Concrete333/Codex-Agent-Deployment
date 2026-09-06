# Agent Deployment

A Codex skill for routing subagent work between two deliberate defaults:

```text
Large context, large-repo exploration, or repetitive work -> Luna at max
Harder, well-specified implementation where correctness matters more -> Astra at low
One substantive Luna failure on a non-trivial task -> Astra at low
```

Terra is not part of this policy. Sol remains available for one consolidated independent review when the risk justifies it.

## Why this split

Luna is cheap enough to absorb large context and repetitive workloads. The skill uses Luna only at `max`, giving those assignments the model's highest supported reasoning effort.

Astra at `low` handles difficult implementation once the behavior, interfaces, scope, and acceptance checks are settled. This spends Astra tokens on judgment and correctness instead of broad repository reading that Luna can do first.

OpenAI lists a 1,050,000-token context window for both models. It describes Luna as designed for cost-sensitive, high-volume workloads and confirms that Luna supports `max`. Astra supports `low` and is OpenAI's most capable model for complex reasoning and coding.

- [GPT-5.6 Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [GPT-6 Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)

## Routing table

| Work | Model and effort | Reason |
| --- | --- | --- |
| Load and search substantial context | Luna at `max` | Context volume dominates the task. |
| Explore or map a large repository | Luna at `max` | Luna can return exact files, symbols, and invariants for the next worker. |
| Apply repetitive or bulk changes | Luna at `max` | The work is broad but objectively verifiable. |
| Implement difficult, settled behavior | Astra at `low` | The task needs stronger judgment and correctness matters more. |
| Review consequential integrated work | Sol, optional | One independent pass can catch cross-module or architectural problems. |

Ordinary small work does not need an agent merely to fill a slot.

## Combined tasks

When a task needs both broad exploration and difficult implementation:

1. Luna at `max` maps the repository, gathers exact evidence, and returns a concise implementation packet.
2. The coordinator settles any remaining design or interface decisions.
3. Astra at `low` implements the specified change.
4. Sol reviews once if the risk warrants independent scrutiny.

This keeps Astra from rereading the whole repository while still giving the harder patch to the stronger model.

## Failure rule

A substantive Luna failure on a non-trivial task ends Luna retries for that task. Preserve the failed check and useful evidence, narrow the contract if needed, and move the implementation to Astra at `low`.

Transient tool or environment failures do not count as model failures. A trivial correction can stay with the coordinator.

## Assignment shape

Give each worker a short, self-contained packet:

```text
Outcome and scope:
Owned files; dependencies and interfaces:
Context entry points and search targets:
Constraints and behavior to preserve:
Acceptance checks and commands:
Return: changed files or evidence, check results, unresolved risks.
```

Do not pass full conversation history or repository dumps. Luna should return exact file, symbol, command, and failure references so Astra can act without repeating the exploration.

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
$agent-deployment Route this delegated task. Use Luna only at max for large-context, large-repo, or repetitive work. Use Astra at low for harder implementation once the task is well specified, and escalate after one substantive Luna failure.
```

The skill chooses deployment roles. It does not authorize delegation, override explicit model choices, or guarantee cost savings.

## Repository contents

- `SKILL.md` contains the routing, context, failure, and review rules.
- `agents/openai.yaml` contains the Codex display metadata and default prompt.

## Sources and acknowledgements

Reddit user [`u/emir_morris`](https://www.reddit.com/user/emir_morris/) proposed the four-tier model ladder and practical model summaries in ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/). That post started this project.

Reddit user [`u/Icy_Piece6643`](https://www.reddit.com/user/Icy_Piece6643/) drew attention to Astra's delegation and prompting behavior in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/). The current policy is an independent adaptation built around context cost, bounded handoffs, and early escalation. It also follows [OpenAI's official Astra guidance](https://developers.openai.com/api/docs/guides/latest-model).
