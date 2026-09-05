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

The skill assigns the lowest-cost model that can own each task without creating extra supervision or rework.

## How it works

Agent Deployment asks Codex to:

1. Split the request into bounded tasks with clear outputs and acceptance checks.
2. Separate discovery difficulty from implementation difficulty.
3. Assign a model to each task instead of pricing the whole project at its hardest tier.
4. Promote tasks with ambiguity, architectural risk, or expensive failure modes.
5. Demote tasks once another agent has turned them into precise, verifiable instructions.
6. Keep final integration with an agent capable of judging the complete result.

The skill guides model selection. Codex follows the user's instructions and creates subagents when the request or project instructions call for delegation.

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

## Scope

This project focuses on model assignment for complex Codex tasks that use subagents. It does not replace project planning, grant permission to delegate work, or make model availability guarantees.
