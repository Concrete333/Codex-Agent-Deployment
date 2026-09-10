# Stronger grading — 10 September 2026

Version 2 retains the thirty original checks and adds nine test methods with
parameterized cases. It tests elapsed-time scheduling across forward/backward
clock changes, HTTP dates across a clock change, equal instants and microsecond
boundaries, fractional/large numeric delays, invalid replacement atomicity,
exact money under limited Decimal precision, distant fractional cents, signed
money boundaries, and three fixed-seed sequences of eighty queue operations.

The queue oracle is a separate list model. Time expectations are calculated
from UTC instants, not from the reference scheduler. These are 39 test methods,
not 39 independent benchmark tasks; no pass percentage establishes production
reliability.

## Contract and reference corrections

[contract-v2.md](contract-v2.md) defines the evaluation's practical numeric
scope and precision. New v2 trials receive it alongside TASK.md. Arbitrary
precision objects such as `Decimal('1e-1000030')` remain optional stress cases,
not required acceptance tests. Exact decimal money is still required.

The reference previously added elapsed seconds to local wall-clock time and
rounded money under the ambient Decimal context. Both are corrected in
`reference.py`. The original reference passed v1 despite those defects; a
reference passing its own grader was not sufficient verification.

`grade.py` and `task/TASK.md` are unchanged. `grade_v2.py` imports the original
checks and adds the new ones. Both corrected reference runs pass. The seeded
implementation fails both versions. The shared runner accepts
`--grader grade_v2.py`, includes the contract in every arm, and records hashes
of the selected grader, underlying v1 grader and contract. No new paid A/B/C
trial was run with v2.

## Saved-artifact results

| Saved artifact | Frozen v1 | Expanded v2 | Interpretation |
| --- | ---: | ---: | --- |
| A: solo | 30/30 | 39/39 | Passes these checks |
| B: unguided delegation | 30/30 | 39/39 | Passes these checks |
| C1: previous skill | 30/30 | 39/39 | Passes these checks |
| C2: revised skill | 30/30 | 37/39 | Still partial; elapsed-time scheduling is wrong |

C2 has three assertion failures across two methods: forward/backward clock
changes and HTTP-date scheduling across a change. Its earlier timeout and
captured cost remain unchanged. No saved implementation was repaired. Production
source hashes in `feed/` and `retryq/` match before/after offline grading.

These are retrospective diagnostics informed by observed defects, not a fresh
holdout evaluation. A/B/C1 passing v2 does not prove they have no other defects.
Use a frozen contract and grader across all arms of the next authorized trial.

## Reproduce offline

```powershell
python -B -X utf8 docs/benchmarks/dual-service/regrade.py A=<saved-A-task-directory> B=<saved-B-task-directory> C1=<saved-C1-task-directory> C2=<saved-C2-task-directory>
```

This runs both graders without models and retains exact failure logs and hashes
in a temporary directory. Local receipts for this pass are in
`agent-deployment-regrade-v2-8d3pxtc6` under the system temporary directory.
Receipts hash production packages, not worker tests.

- V1 SHA-256: `ff9ab60d9bd5364b197496c97d53ed3e4b7ee2d75b7d8ec876afbdc3f08c12d0`.
- V2 SHA-256: `279fbb563380d474648ad990ee436670940f64c9d1cd01bee838641a03cd4b71`.
