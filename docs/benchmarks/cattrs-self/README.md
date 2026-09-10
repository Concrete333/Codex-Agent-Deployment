# Repository-scale type-resolution upgrade

Upgrade `typing.Self` support in a pinned [cattrs](https://github.com/python-attrs/cattrs)
checkout. The baseline has about 5,180 nonblank Python source lines across real
conversion, code-generation and dispatch modules, plus its existing tests and
documentation. This is a larger candidate for bounded delegation, not a task
that requires or guarantees it.

See the [A/B/C results](results-2026-09-10.md): the current skill delegated to
Luna Max, but did not lower total cost on this task.

Attrs/dataclass generation, TypedDict generation and NamedTuple dictionary
factories provide distinct investigation/implementation paths. Shared type
resolution and final integration remain coordinator responsibilities. No padding,
forced worker count or hints identifying the required patch are added.

## Frozen scope

- Baseline: cattrs 24.1.3, commit `ec5383376ced63c1dfb8d98b9307f7226c98d53a`.
- Python 3.12; exact dependencies in `requirements-lock.txt`.
- Same `TASK.md`, starting tree and fifteen-minute process limit for A/B/C.
- Astra High coordinator. A disables delegation; B allows native GPT delegation
  without the skill; C supplies the current skill. Claude is excluded from B/C.
- Sixteen external feature cases: eight behaviors in both validation modes.
  Another 265 frozen baseline regression cases must pass. Existing tests cannot
  be weakened by a submission; grading reads them from the untouched baseline.
- Delegation remains optional. Scripts and targeted searches are allowed in
  every arm. Count all parent/child usage and failures, not only worker costs.

The feature cases fail on the baseline (14 errors, two already-passing isolation
checks) and pass on upstream 25.1.0, commit
`9122f10a5cdbb7d1c2449e39fabbaf51b8cffe53`. The 265 regression checks pass on
the 3.12 baseline. A 3.13 preparation attempt exposed two unrelated existing
generic-conversion failures, so 3.12 was selected before any paid trial.

The later release is only a feature-check reference: its removed private
compatibility aliases make some old regression modules unimportable. It is
not presented as a passing full submission. The required new behavior is
consistent with upstream's [Self tests](https://github.com/python-attrs/cattrs/blob/9122f10a5cdbb7d1c2449e39fabbaf51b8cffe53/tests/test_self.py).

This is a published feature on public code, so training-data familiarity is
possible. It is a development benchmark, not an unseen standardized holdout.
No live network, future upstream source or other trials may be consulted by
participants. The downloaded source retains its upstream MIT license.

## Prepare and run

```powershell
python docs/benchmarks/cattrs-self/prepare.py --python C:/path/to/Python312/python.exe
python docs/benchmarks/pilot/run.py C --suite docs/benchmarks/cattrs-self --source <printed-baseline-path> --python <printed-python-path> --prepare-only
```

Preparation downloads source/dependencies, but calls no models and changes no
global Python packages. It writes a git-ignored `local-fixture.json`; regenerate
it on another machine. Removing `--prepare-only` starts a paid run. Use A, B or
C only as authorized. The grader uses the sandbox's read-only command mode so
new sandbox-owned files can be imported without changing their permissions.

All models see the same complete repository and checks they may run. Only C gets
the routing skill. Raw traces and submissions remain in private system-temp
directories. Configuration and final team usage must be audited before comparing
cost. The safety limit can censor a slow attempt; elapsed time is not a success
metric. Keep preparation/supervision separate from trial costs.
