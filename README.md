# Agent Deployment

A Codex skill for deciding which model should do the work, how much work to give it, and when to step in. The goal is to spend less getting a correct result, including the cost of reviews and retries.

```text
Bounded context gathering or repetitive work -> Luna Max
Uncertain cause or design -> Sol High
Non-mechanical, specified implementation -> Astra Light
One substantive Luna failure or failed Sol diagnosis -> Astra Light
Review for important correctness problems -> Astra
Targeted edge-case / hardening review -> optional Sol High
```

Model settings: Luna Max = `gpt-5.6-luna` / `max`; Sol High = `gpt-5.6-sol` / `high`; Astra Light = `gpt-6-astra` / `low`.

## Routing

| Work | Model and effort | Expected result |
| --- | --- | --- |
| Search substantial context or map a repository | Luna Max | File references, search coverage, and open questions |
| Apply repetitive changes with objective checks | Luna Max | Changes within the assigned scope, with check results |
| Find an unclear cause or work out a design | Sol High | A diagnosis supported by evidence and a clear implementation brief |
| Implement specified behavior beyond mechanical edits | Astra Light | Working code and checks for the required behavior |
| Take over after one substantive Luna failure or failed Sol diagnosis | Astra Light | Use the existing evidence, resolve what remains unclear, and finish the authorized work |
| Review important correctness problems | Astra coordinator at its existing effort, or Astra Light if a separate reviewer is needed | Defects that affect required behavior; the coordinator decides whether to accept the result |
| Check edge cases and harden specific areas | Sol High, optional | Evidence of problems within the assigned release, security, or robustness checks |

Choose by the work, not the size of the repository. Give Sol the diagnosis of a subtle concurrency bug, even in a large codebase. Luna can gather evidence if that saves the next worker a substantial search. Skip that step if the coordinator has enough evidence. For small tasks, keep the work with the current agent when a handoff would cost more than it saves.

Ask Sol for checks that distinguish between possible causes, what remains uncertain, and a proposed implementation brief. A diagnosis assignment doesn't include production changes. Give it a defined scratch or test area if reproduction needs edits. Reviewers inspect without changing files; the implementation owner makes corrections, then someone rechecks the affected behavior. Choose a different reviewer if the review needs independence from the original diagnosis or design.

For either reviewer, ask where the problem is, what triggers it, what it breaks, and what evidence supports the finding. Judge the findings by their impact rather than their number. A rare security or data-loss case can still be critical. Keep confirmed defects separate from optional hardening and ideas that need more evidence.

For mechanical changes with strong checks, skip the extra reviewer. Give Sol High a hardening pass when you can name the risks that warrant one; a release doesn't need that pass by default. Increase Sol to Max for a specific reasoning problem it hasn't resolved, or if you request Max. An Astra High coordinator keeps the final review at High. Don't add another Astra to repeat that review.

## What counts as failure?

Escalate after one substantive failure of a bounded, non-trivial Luna assignment or a Sol diagnosis. A failing test during implementation doesn't count on its own, including a regression test written before the fix. Luna can handle trivial corrections without a handoff.

Let workers correct their work within the agreed budget. They should stop and report if they repeat a failed approach without new evidence or reach a hard limit. At a checkpoint, useful progress can justify a revised estimate within your limits. Taking longer than expected doesn't prove the model has failed. Workers should report unmet acceptance checks, wrong assumptions, missed requirements, and useful partial work.

After a substantive non-trivial Luna failure or a substantive Sol diagnosis failure, give the unresolved work to Astra Light. Treat temporary tool errors and external blockers as separate problems. A reviewer who finds defects has done the job. If Astra fails too, inspect the cause before increasing effort or adding workers. The coordinator makes those decisions; workers need assigned permission to delegate their work.

## Waiting and worker health

Use the runtime's event wait while workers run and the coordinator has no separate useful work to do. Wait for completion or a blocker instead of checking status on a timer.

Use 25 minutes (`1500000` ms) as a starting point if the runtime supports it and higher-priority instructions permit it. Adjust for checkpoints and deadlines, including longer waits where appropriate. If the runtime or responsiveness rules require shorter waits, use the longest suitable interval they allow. Don't add a status check or interrupt the worker after each timeout.

A timeout with no update tells you little about the worker. Keep waiting unless a blocker, checkpoint, or spent budget requires a decision. Don't wake the coordinator to preserve the cache.

For substantial assignments, agree on a rough duration and a checkpoint or work budget. Workers should report blockers as they arise and send a short update at a checkpoint if they can. Don't interrupt a blocking tool to send an update, or ask workers for recurring "still running" messages.

At a checkpoint without a useful update, make one short status check that doesn't interrupt the worker, if the runtime supports it. Look at completed milestones, current operations, and the remaining budget before deciding to continue, narrow the assignment, or stop. A "running" flag doesn't prove progress. This policy uses event waits, not scheduled automations.

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

Give new workers the history they need for the assignment, including relevant instructions and permissions. Reuse a suitable worker to continue within the same scope. Keep handoffs short while preserving exact failures and evidence needed for a decision; link to longer artifacts. Sol and Astra should inspect the relevant source before judging correctness.

Before a replacement edits the same files, confirm that the previous worker and any commands that can write there have stopped. Keep its partial changes and your unrelated edits. Hand over the current diff, evidence, check results, and open questions. Don't let the old and new workers write to the same files at the same time.

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
$agent-deployment Plan the workers for this authorized task. Use Luna Max for scoped searches or repetitive edits, Sol High for diagnosis, and Astra Light for other specified implementation or escalation. Use Astra to review correctness and Sol High for hardening if the risks warrant it. Set checkpoints and wait for events instead of polling.
```

Using this skill grants no permission to delegate or expand a task. The agent must follow the task's existing permissions, higher-priority instructions, and your new explicit choices. It must check which models and effort levels the runtime supports before dispatch. Measure savings on your own work; this skill makes no guarantee.

Read `SKILL.md` for the full policy. `agents/openai.yaml` holds the Codex display metadata; you don't need extra reference files to use the skill.

## Sources and acknowledgements

### Human-reference benchmark workbook

[GPT model efficiency, 8 September 2026](docs/benchmarks/GPT-model-efficiency-2026-09-08.xlsx) contains the selected Artificial Analysis chart data, source links, missing-data flags, and calculated efficiency ratios. The workbook is for human reference. Agents must not load or parse it. Don't use the API benchmark costs to infer Codex allowance usage or coding-task success rates.

### Credits

- [u/emir_morris](https://www.reddit.com/user/emir_morris/): model-role inspiration from ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/).
- [u/Icy_Piece6643](https://www.reddit.com/user/Icy_Piece6643/): prompting and delegation guidance in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/).
- [tagorr](https://github.com/tagorr): polling telemetry in [Codex issue #35259](https://github.com/openai/codex/issues/35259#issuecomment-5577073962).
- OpenAI: [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model) and model documentation for [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), and [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
