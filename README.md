# Agent Deployment

A cost-first Codex skill that uses Astra to plan and review, Luna for most implementation, and Sol to review each iteration.

```text
Astra plan -> Luna implementation -> Sol review -> Luna correction -> Astra final review
```

The basic idea is simple: spend premium-model time where judgment has the most leverage. Astra decides what should be done and judges the finished result. Luna does the work. Sol catches problems while they are still cheap to fix.

## Default roles

| Role | Model | What it does |
| --- | --- | --- |
| Initial planner | Astra (`gpt-6-astra`) | Inspects the task, resolves uncertainty, and produces bounded assignments with dependencies and acceptance checks. |
| Implementation worker | Luna (`gpt-5.6-luna`) | Handles almost all implementation. Increase its reasoning effort when the work gets harder. |
| Iterative reviewer | Sol (`gpt-5.6-sol`) | Reviews each meaningful Luna batch and returns evidence-backed corrections. |
| Final reviewer | Astra (`gpt-6-astra`) | Judges the integrated result against the original goal and either accepts it or requests bounded corrections. |
| Exception implementer | Terra (`gpt-5.6-terra`) | Steps in only when Luna is unavailable or repeatedly fails a narrowed assignment. |

## Luna reasoning effort

The skill promotes Luna's reasoning effort before promoting the implementation model:

| Effort | Typical work |
| --- | --- |
| `low` or `medium` | Renames, boilerplate, copy changes, lint fixes, and routine edits. |
| `high` | Normal features, endpoints, integrations, and tests. |
| `xhigh` | Difficult but bounded debugging or changes across several modules. |
| `max` | The toughest implementation jobs when the scope and acceptance checks are still clear. |

This is an intentional cost tradeoff. OpenAI describes Luna as suited to cost-sensitive, high-volume workloads, and Luna supports both `xhigh` and `max` reasoning. That makes it practical to give Luna several focused attempts while keeping stronger judgment around the work. See the [official GPT-5.6 Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

Repository size does not decide the model. A large, exact task can still be Luna work. What matters is whether the assignment is bounded and testable.

## How the loop works

1. Astra inspects the goal and produces the initial task graph.
2. The coordinator turns that plan into bounded Luna assignments.
3. Independent Luna agents work in parallel when they do not share files or unfinished dependencies.
4. Sol reviews each meaningful implementation batch.
5. Luna applies Sol's corrections.
6. The Luna and Sol loop continues until Sol finds no material issue or the escalation rule applies.
7. Astra reviews the complete result, review history, and verification evidence.
8. Any final correction goes back to Luna before Astra makes the final decision.

Keep integration ownership with the coordinating agent. Correct subtask outputs can still conflict when combined.

## Escalation rule

If Luna fails the same acceptance check twice, Sol rewrites the assignment with narrower scope and stronger evidence. If Luna fails that revised assignment, Terra can take the implementation task as an exception.

Astra does not become the implementation worker by default. Its time stays concentrated at the two points where broad judgment matters most: the plan and the final review.

## Example deployment

For an offline-sync bug that creates duplicate records without reliable reproduction steps:

| Stage | Model | Assignment |
| --- | --- | --- |
| Initial plan | Astra | Locate the uncertainty, define the investigation, split the work, and state the acceptance checks. |
| Implementation | Luna at `xhigh` | Reproduce the bug, implement the bounded fix, and add regression coverage. |
| Iterative review | Sol at `xhigh` | Check the root-cause claim, cross-module effects, and test evidence. |
| Correction | Luna at `xhigh` or `max` | Apply Sol's bounded corrections and rerun the required checks. |
| Final review | Astra | Compare the integrated result with the original goal and accept it or request a final bounded correction. |

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
$agent-deployment Build a cost-first agent team for this task. Use Astra to plan and give final review, Luna for implementation, and Sol for iterative review.
```

You can also ask it to review an existing deployment:

```text
$agent-deployment Check whether this plan keeps implementation with Luna, gives Sol clear review contracts, and reserves Astra for the initial plan and final review.
```

The skill selects roles and reasoning effort. Codex still follows your instructions and only creates subagents when you or the active project instructions authorize delegation.

## Repository contents

- `SKILL.md` contains the deployment rules, review contracts, and escalation policy.
- `agents/openai.yaml` provides the Codex display name and default prompt.

## Sources and acknowledgements

Reddit user [`u/emir_morris`](https://www.reddit.com/user/emir_morris/) proposed the four-tier model ladder and its practical model summaries in ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/). That post gave me the starting point for thinking about task difficulty and model choice.

Reddit user [`u/Icy_Piece6643`](https://www.reddit.com/user/Icy_Piece6643/) drew attention to Astra's delegation and prompting behavior in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/). This project turns those ideas into a cost-first deployment loop rather than reproducing either post. The Astra-specific guidance also follows [OpenAI's official model guidance](https://developers.openai.com/api/docs/guides/latest-model).

## Scope

This project focuses on model and reasoning-effort assignments for complex Codex tasks with subagents. It does not replace project planning, grant permission to delegate, or guarantee that every model is available in every environment.
