# Agent Deployment

A Codex skill for assigning Luna, Terra, Sol, or Astra to each part of a multi-agent task based on uncertainty, implementation difficulty, and verification cost.

Complex projects can need several models. An unknown production bug may need Astra to find the problem, Sol to implement the fix, Terra to add routine coverage, and Luna to handle exact follow-up edits. Agent Deployment gives Codex a consistent way to make those assignments.

## Model ladder

| Model | Use it when | Short version |
| --- | --- | --- |
| Luna (`gpt-5.6-luna`) | You know the target, method, and acceptance check. The work consists of renames, boilerplate, copy changes, lint fixes, or repetitive edits. | We know what to do. Use the low-cost model. |
| Terra (`gpt-5.6-terra`) | The task follows familiar development patterns, such as screens, endpoints, existing API integrations, and straightforward tests. | Normal software development. |
| Sol (`gpt-5.6-sol`) | You understand the goal, but the implementation or debugging work is difficult and spans existing architecture. | The implementation is hard. |
| Astra (`gpt-6-astra`) | The agent must locate the problem, determine the right approach, make architectural tradeoffs, or perform a nuanced review. | Figuring out what to do is hard. |

The skill optimizes for the expected total cost of a correct result. It considers token use, retries, supervision, and rework instead of comparing token prices alone.

## How it works

Agent Deployment asks Codex to:

1. Split the request into bounded tasks with clear outputs and acceptance checks.
2. Separate discovery difficulty from implementation difficulty.
3. Assign a model to each task instead of pricing the whole project at its hardest tier.
4. Treat open-ended inspect, run, observe, revise, and verify loops as an Astra signal.
5. Promote tasks with ambiguity, architectural risk, or expensive failure modes.
6. Demote tasks once another agent has turned them into precise, verifiable instructions.
7. Keep final integration with an agent capable of judging the complete result.

The skill guides model selection. Codex follows the user's instructions and creates subagents when the request or project instructions call for delegation.

Repository size and context length do not determine the model. A large batch of exact edits can remain Luna work. Cross-system uncertainty or long-horizon decisions may require Astra.

## Astra assignments

An Astra prompt should state the objective, owned scope, dependencies, required output, acceptance checks, and stopping condition. It should also say whether Astra may delegate, which work can run in parallel, and whether its subagents may delegate again.

The prompt should tell Astra to finish authorized work through proportionate verification. Astra can make routine, reversible assumptions and should ask for user input when missing information could change correctness, scope, or authorization. Targeted checks suit small changes; failures and unresolved concerns justify broader testing.

## Example deployment

For a report that an offline-sync system creates duplicate records with no known reproduction steps:

| Task | Model | Reason |
| --- | --- | --- |
| Reproduce and localize the failure | Astra | The cause and owning subsystem are unknown. |
| Implement the cross-module fix | Sol | The investigating agent identified the root cause, but the change remains difficult. |
| Add routine endpoint and fixture coverage | Terra | The interfaces and expected behavior are clear. |
| Rename affected helpers and update imports | Luna | The edits are exact and easy to verify. |
| Review the integrated result | Sol or Astra | The reviewer must assess interactions across the full change. |

## Installation

Clone the repository into your personal Codex skills directory.

macOS or Linux:

```bash
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git ~/.codex/skills/agent-deployment
```

Windows PowerShell:

```powershell
git clone https://github.com/Concrete333/Codex-Agent-Deployment.git "$env:USERPROFILE\.codex\skills\agent-deployment"
```

## Usage

Invoke the skill in Codex:

```text
$agent-deployment Plan a subagent deployment for this task, choose a model for each assignment, and explain each choice.
```

You can also ask it to review an existing plan:

```text
$agent-deployment Check this delegation plan for agents that are overpowered, underpowered, or carrying tasks with unclear acceptance criteria.
```

## Repository contents

- `SKILL.md` contains the model-selection rules and deployment method.
- `agents/openai.yaml` provides the Codex display name and default prompt.

## Sources and acknowledgements

Reddit user [`u/emir_morris`](https://www.reddit.com/user/emir_morris/) proposed the original four-tier model ladder, summaries, and examples in ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/). This skill adapts that framework into deployment instructions for Codex.

Reddit user [`u/Icy_Piece6643`](https://www.reddit.com/user/Icy_Piece6643/) highlighted Astra's prompting behavior in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/). The deployment refinements also follow [OpenAI's official GPT-6 Astra model guidance](https://developers.openai.com/api/docs/guides/latest-model).

## Scope

This project focuses on model assignment for complex Codex tasks that use subagents. It does not replace project planning, grant permission to delegate work, or make model availability guarantees.
