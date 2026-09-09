# Local A/B/C smoke test

One custom Python cache-repair task, three conditions, no dependencies beyond
Python, Git and the installed Windows Codex CLI. This is a harness smoke test,
not a standard benchmark or a statistically reliable model comparison.

| Condition | Coordinator | Delegation | Deployment skill |
| --- | --- | --- | --- |
| A | Astra High | Disabled | Not supplied |
| B | Astra High | Native GPT workers allowed | Not supplied |
| C | Astra High | Same native GPT workers allowed | Explicitly supplied |

Run each condition separately:

```powershell
python docs/benchmarks/pilot/run.py A
python docs/benchmarks/pilot/run.py B
python docs/benchmarks/pilot/run.py C
```

`--prepare-only` creates a fresh copy and manifest without calling a model.
Each run has a 15-minute process-tree timeout. B/C allow at most two concurrent
children and use the same 25-minute event-wait settings. Neither condition is
required to delegate. Claude is excluded from this first pilot in both B and C.

The runner ignores user configuration and execpolicy rules, disables discovered
skills, plugins and memory, and retains existing ChatGPT authentication. Global
AGENTS instructions remain present and must be held constant across conditions. It uses
workspace-write sandboxing, disables web search, and does not change global
settings. Inspect the recorded initial context to confirm isolation; suppressing
host skill discovery alone does not disable local skills. C receives a snapshot
of the operational skill and references in `.benchmark-policy` inside its task
checkout, not research documents. An unreadable policy blocks C rather than
silently converting it into another no-skill run.

The task starts with two passing public tests and seeded cache defects. Twelve
requirement-derived acceptance tests live outside the worker checkout. The
reference implementation passes all twelve; the starting implementation fails.
Workers are instructed not to inspect the grader or other trials. This is not
an adversarially secured benchmark: filesystem read isolation is not guaranteed.

Every run retains its task copy, starting Git tree, configuration, prompt, JSONL
events, stderr, patch, grading output and result in a unique system-temp folder.
Native rollouts remain in Codex's session storage. Keep raw traces private and
outside this repository; the runner prints their local run directory.

Final CLI usage alone must not be assumed to include every child. Reconcile
root and child rollouts, effective model/effort, cache reads/writes and tool
activity before comparing full-workflow cost. API-equivalent estimates are not
subscription charges. Report setup/evaluation overhead separately from trial
cost, and compare acceptance rate alongside cost. Repeat on new tasks and vary
run order before drawing deployment conclusions.
