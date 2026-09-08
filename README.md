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

Use `gpt-5.6-luna` at `max` for all Luna assignments, even if an older preference says High or X-High. This policy leaves Terra out.

Astra Light uses `gpt-6-astra` with reasoning effort `low`.

## Why these defaults

OpenAI describes Luna as a model for cost-sensitive, high-volume work, Sol as a flagship for complex professional work, and Astra as its most capable model for complex reasoning and coding. I use those descriptions as a starting point. They don't tell us which effort level is best for a particular job.

The defaults here are Luna Max, Sol High, and Astra Light. Judge them by the cost of finishing work that passes its checks, including coordination, reviews, and corrections. A model can use more tokens and still cost less. Models with the same context window can differ in reasoning ability, and Max effort can still produce a wrong answer. Before claiming savings, compare accepted results, total usage, elapsed time, corrections, and missed defects. Keep separate measurements for API costs and Codex allowance usage.

- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)

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

In my own use, Astra seems better at spotting larger problems. Sol tends to find more edge cases. That's anecdotal, and I haven't established that Sol is a better security auditor. For either model, ask where the problem is, what triggers it, what it breaks, and what evidence supports the finding. Judge the findings by their impact rather than their number. A rare security or data-loss case can still be critical. Keep confirmed defects separate from optional hardening and ideas that need more evidence.

For mechanical changes with strong checks, skip the extra reviewer. Give Sol High a hardening pass when you can name the risks that warrant one; a release doesn't need that pass by default. Increase Sol to Max for a specific reasoning problem it hasn't resolved, or if you request Max. An Astra High coordinator keeps the final review at High. Don't add another Astra to repeat that review.

## What counts as failure?

Escalate after one substantive failure of a bounded, non-trivial Luna assignment or a Sol diagnosis. A failing test during implementation doesn't count on its own, including a regression test written before the fix. Luna can handle trivial corrections without a handoff.

Let workers correct their work within the agreed budget. They should stop and report if they repeat a failed approach without new evidence or reach a hard limit. At a checkpoint, useful progress can justify a revised estimate within your limits. Taking longer than expected doesn't prove the model has failed. Workers should report unmet acceptance checks, wrong assumptions, missed requirements, and useful partial work.

After a substantive non-trivial Luna failure or a substantive Sol diagnosis failure, give the unresolved work to Astra Light. Treat temporary tool errors and external blockers as separate problems. A reviewer who finds defects has done the job. If Astra fails too, inspect the cause before increasing effort or adding workers. The coordinator makes those decisions; workers need assigned permission to delegate their work.

## Waiting and worker health

Use the runtime's event wait while workers run and the coordinator has no separate useful work to do. Wait for completion or a blocker instead of checking status on a timer.

Use 25 minutes (`1500000` ms) as a starting point if the runtime supports it and higher-priority instructions permit it. Adjust for checkpoints and deadlines, including longer waits where appropriate. If the runtime or responsiveness rules require shorter waits, use the longest suitable interval they allow. Don't add a status check or interrupt the worker after each timeout.

A timeout with no update tells you little about the worker. Keep waiting unless a blocker, checkpoint, or spent budget requires a decision. Don't wake the coordinator to preserve the cache. OpenAI documents at least 30 minutes of cache eligibility, with longer periods possible. That doesn't establish Codex allowance costs or the best wait interval. [Official caching documentation](https://developers.openai.com/api/docs/guides/prompt-caching)

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

[GPT model efficiency, 8 September 2026](docs/benchmarks/GPT-model-efficiency-2026-09-08.xlsx) contains the selected Artificial Analysis chart data, source links, missing-data flags, and calculated efficiency ratios. We keep it here for people to read. Agents must not load or parse the workbook, and the skill runs without it. Don't use the API benchmark costs to infer Codex allowance usage or coding-task success rates.

Reddit user [`u/emir_morris`](https://www.reddit.com/user/emir_morris/) proposed the four-tier model ladder and practical model summaries in ["GPT-6 Astra: Everything You Need to Know"](https://www.reddit.com/r/codex/comments/1w6rqgf/gpt6_astra_everything_you_need_to_know/). That post started this project.

Reddit user [`u/Icy_Piece6643`](https://www.reddit.com/user/Icy_Piece6643/) drew attention to Astra's delegation and prompting behavior in ["Before blaming GPT-6 Astra, read its prompting guide"](https://www.reddit.com/r/codex/comments/1w7x57n/before_blaming_gpt6_astra_read_its_prompting_guide/). I adapted those ideas into rules for context costs, bounded handoffs, and early escalation, alongside [OpenAI's official Astra guidance](https://developers.openai.com/api/docs/guides/latest-model).

GitHub user [`tagorr`](https://github.com/tagorr) documented 47 empty 30-second `wait_agent` polls that caused 7.13 million Astra parent input tokens in [OpenAI Codex issue #35259](https://github.com/openai/codex/issues/35259#issuecomment-5577073962). We found the same mechanism in our saved Codex rollouts, though the intervals and percentages differed. Those checks led us to add the rule against avoidable status polling.
