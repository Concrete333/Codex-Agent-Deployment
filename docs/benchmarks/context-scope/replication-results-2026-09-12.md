# Search-scope replication

Both guided workers passed the same exact checks as their controls at lower
recorded cost. The evidence supports a narrow search-assignment heuristic,
not a measured improvement to full implementation or orchestration.

## Setup

Four fresh **Luna Max** sessions, one per cell, in fees A/B then funding B/A
order. A uses the existing bounded assignment. B appends the exact paragraph
in the [procedure](README.md). Model, effort, tools, task, source and checker
were otherwise fixed. There was no model reviewer, orchestrator or retry in
the measured worker workflow.

The original source-only snapshot was reused: 238 files, 7,700,300 bytes, with
88 production Python files. No prior worker answers were copied. Each worker
inventoried every literal `.get(...)` call for its assigned setting keys, with
path, line and full expression. The fee task has 14 matches; funding has three.
Those counts were not supplied to the workers.

Each fresh checkout passed a no-model sandbox shell-cwd preflight. Both actual
sandbox graders also passed before spending. New request identities, exclusive
start marker and a frozen code/request/source manifest are retained privately.
The previous aborted experiment remains separate; its costs are not a baseline
for this replication. No live Spaceships files or sandbox ACLs were changed.

## Results

| Task | Existing packet A | Search-guided B | Reduction | Exact acceptance |
|---|---:|---:|---:|---|
| Fees | $0.02762 | $0.02198 | 20.4% | Both passed 14/14 |
| Funding | $0.02548 | $0.01790 | 29.7% | Both passed 3/3 |
| Combined | $0.05310 | $0.03988 | **24.9%** | All four passed |

Total recorded worker cost: **$0.09299 historical API-equivalent**. These use
the frozen rates in `revision-ab/summarize.py`, not current prices, actual
bills or subscription consumption. Research preparation, this supervising
conversation, its waiting/updates, and offline grading are excluded. This is
not an end-to-end savings claim. All four native own-session usage records
reconcile and confirm Luna Max.

| Combined measure | A | B |
|---|---:|---:|
| Input tokens, including cached input | 413,379 | 394,104 |
| Cached input tokens | 282,624 | 328,960 |
| Other input tokens | 130,755 | 65,144 |
| Output tokens, including reasoning | 17,751 | 16,896 |
| Model responses | 21 | 21 |
| Captured tool-output characters | 63,453 | 46,730 |
| Explicitly truncated returns | 1 | 0 |
| Compactions | 0 | 0 |

Tool-output text fell 26.4%, while total input fell only 4.7%. Cache behavior
accounts for part of the cost difference. Character counts are not billed
tokens. The fee treatment used more responses (11 vs 8); the funding treatment
used fewer (10 vs 13). No general reduction in model turns was demonstrated.

## Acceptance and observed problems

The host's exact AST-based checker accepted every inventory and verified the
protected source hashes. Required artifact and handoff hashes stayed unchanged
through final checking. No worker exited partial or needed a paid correction.
The fee treatment's flagged dynamic-key exclusion agrees with the contract's
literal-key-only scope; it is not an unresolved defect. Control handoffs saying
the host check was pending were superseded by the saved passing host receipts.

Two tool problems remain part of the reported costs:

- Fees B tried `py`, which selected an inaccessible Windows Store Python. It
  recovered using another interpreter.
- Funding A omitted its cell directory from one `workdir` argument. The process
  failed to start with error 267; the worker corrected the path. This was not
  the old silent fallback to `C:\`: the requested path itself was wrong, and
  no command ran in that failed call.

These were different, local worker errors, not controlled interventions. They
add noise and prevent attributing the full dollar difference to search wording.
They are not removed from costs after seeing the results. The fee control also
ran a broad `.get(` search before using an exact AST extractor and manually
copied extracted rows into its artifact. That suggests a separate future test
of direct machine-written extraction, not another change bundled into this one.

## Skill change

Added the exact tested paragraph to `references/delegation.md`, conditional on
repository-search assignments. It tells workers to locate candidate files,
read relevant ranges, recover truncated evidence and widen search for coverage.
It adds no research or benchmark claims to operational context. Model routing,
effort, ownership and verification remain unchanged. The installed guide was
synchronized after validation.

This is provisional guidance based on two small tasks, one run per arm, with
uncontrolled sampling and cache state. It does not establish semantic review
accuracy, skill-driven spontaneous routing, delegation beating solo work, or
unchanged accuracy on implementation tasks. It also does not measure whether
shortening this paragraph would preserve the result.

## Next test

Use a held-out bounded component change with caller/test interactions and
independent hidden checks. Keep the same worker model and compare ownership
through implementation and corrections against a handoff between phases, with
all preparation, integration and correction cost counted. Do not deliberately
use a weak baseline; specify both workflows before running.

A checkpoint-resumption comparison needs a task that actually loses useful
context; none of these workers compacted. Do not claim this result tests it.
No additional paid tests were launched after the four frozen cells.
