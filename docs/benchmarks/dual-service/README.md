# Independent-component repair test

One custom Python task with two independent packages: a transaction CSV importer
and a retry scheduler. Both have fixed interfaces and seeded defects. This gives
delegation a useful opportunity without requiring it. It is not a standard coding
benchmark or a sample of thirty independent tasks.

See the [9 September results](results-2026-09-09.md) for measured team usage and
external acceptance results, and the [10 September C repeat](results-2026-09-10.md)
for the revised worker policy, timeout outcome and short-sleep overhead.
The [C3 repeat](results-c3-2026-09-10.md) uses the current skill and v2 contract:
the coordinator chose solo execution and passed all 39 expanded checks.

The frozen v1 grader has thirty test cases. [Version 2](grading-v2.md) retains
those and adds nine boundary/state checks. The corrected reference passes both;
the starting implementation does not. The [offline regrade](grading-v2.md#saved-artifact-results)
compares the same saved A/B/C1/C2 artifacts without new model runs.
Workers receive the requirements, source and two public smoke tests, not the
grader or reference solution. They must add their own regression tests.

## Run

From the repository root:

```powershell
python -X utf8 docs/benchmarks/dual-service/grade.py --reference -q
python -X utf8 docs/benchmarks/dual-service/grade_v2.py --reference -q
python -X utf8 docs/benchmarks/pilot/run.py C --suite docs/benchmarks/dual-service --grader grade_v2.py --prepare-only
```

Grading and `--prepare-only` do not call models. Removing `--prepare-only` starts
a paid-model run using the existing Codex login. Use A, B or C as authorized;
each gets a fresh task copy and a fifteen-minute safety limit. Version-2 trials
supply the same numeric/time contract to every condition and record its hash.
Omit `--grader grade_v2.py` only to reproduce the historical v1 setup.

- **A:** Astra High alone, delegation disabled, no deployment skill.
- **B:** Astra High with optional native GPT delegation, no deployment skill.
- **C:** The same coordinator and worker pool, with the current deployment skill.

The shared [runner controls](../pilot/README.md) apply. Claude is excluded from
both delegation conditions. Raw logs and task copies remain in the system
temporary directory; inspect the printed run paths. Audit worker rollouts as
well as the coordinator: the coordinator's reported usage is not a whole-team
cost. Compare acceptance and total team usage, not elapsed time alone.
