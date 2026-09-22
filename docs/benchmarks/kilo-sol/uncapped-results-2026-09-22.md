# Uncapped MiMo: complete handoff, lower cost, unresolved reference mismatch

The fresh Sol High -> MiMo-V2.6-Pro thinking -> resumed Sol High run completed
normally. MiMo returned a valid handoff in **22 steps**, with no wrapper issues,
timeout or unresolved ownership. Its manifest has `steps: null`; the resolved
profile confirms no iteration cap. Because this run used fewer than 30 steps,
it does **not** demonstrate that removing the old cap caused the improvement.

Both worker and final submissions passed all 146 visible and 98 held-out cases,
plus 53 added tests. Sol accepted without corrections; all eight worker-owned
files are byte-identical to the final submission. However, the post-hoc CSV quote
probe still differs from the frozen reference, as detailed below.

## Execution cost

| Arm | Sol estimate | Worker cost | Combined | Frozen suite |
| --- | ---: | ---: | ---: | ---: |
| Sol High solo | $0.776054 | — | $0.776054 | 244/244 |
| Sol + capped MiMo | $0.683719 | $0.149495 | $0.833214 | 244/244 after repair |
| Sol + Luna Max | $0.450906 | $0.091826 | **$0.542732** | 244/244, no repairs |
| Sol + uncapped MiMo | $0.557435 | $0.126490 | **$0.683925** | 244/244, mismatch below |

The uncapped run cost 11.871% less than the retained solo baseline on this
accounting basis. This is cost to the pipeline's acceptance, **not a demonstrated
equally correct result** once the reference mismatch is considered. Luna remains
the cheapest observed pipeline and rejects the quote probe without repair.

| Uncapped stage | Cost | Process duration |
| --- | ---: | ---: |
| Sol preparation | $0.108059 | 119.538 s |
| MiMo implementation | $0.126490 | 756.270 s |
| Sol acceptance | $0.449376 | 315.748 s |

Sol's combined recorded usage: 260,621 input tokens including 196,608 cached;
11,137 output tokens including reasoning; 12 responses. Per-response records
reconcile to cumulative session usage and confirm `gpt-5.6-sol / high`.
MiMo model/variant and uncapped configuration are recorded in its manifest and
resolved profile. Its cost is provider-reported; Sol is API-equivalent using the
existing benchmark rates. Neither is a subscription-allowance measurement.
Research setup, supervision and analysis are excluded. No paid retries occurred.

## The accuracy caveat

On the same post-hoc input used for the other runs:

```text
id,date,amount,currency,memo
a,2024-02-29,1,USD,x"y
```

- The frozen reference rejects with `ValueError`.
- Sol solo and Sol/Luna reject.
- The capped MiMo worker accepted; Sol added validation before acceptance.
- The uncapped MiMo worker accepts; Sol knowingly accepted that behavior too.

MiMo explicitly reported this judgment call. Sol accepted its argument that
`csv.reader(strict=True)` allows the quote and that the task does not explicitly
settle that edge. TASK.md says malformed CSV quoting is invalid but supplies no
full grammar or concrete bare-quote example. The reference's intended rejection
was present before the trial, yet absent from the 244 graded cases.

Record this as a **reproduced reference mismatch and inconsistent acceptance
interpretation**, not a frozen-suite failure. The result does not prove there
was no accuracy loss. Nor does the disagreement alone establish that a broader
model family is unreliable. Sol's two reviews reached different conclusions;
more tests or a complete handoff did not resolve the contract interpretation.

The measured artifact is unchanged. No after-the-fact repair or relaxed checker
has been included in the original cost. A future fixture should state the quote
rule explicitly and include it in grading before model work begins. Such a known
case would be regression coverage, not a new held-out capability test.

## Interpretation and limits

This is a productive MiMo run, unlike the earlier no-artifact production attempts.
It demonstrates complete delivery through the uncapped wrapper. It does not
isolate the effect of removing the cap: the new run used 22 steps, model outputs
vary, and line-ending/acceptance-schema fixes also differ from the original arm.
The two fresh follow-ups share those runtime fixes. See
[the protocol](uncapped-protocol-2026-09-22.md).

One run per arm on a reused fixture supports no general ranking. Do not weaken
verification or change routing solely on these prices. The best observed result
in this set is Sol/Luna, but replication on a clarified or genuinely held-out
task is needed before claiming reliable savings without reduced accuracy.

## Evidence

Local root: `C:/Users/cwbec/AppData/Local/Temp/sol-mimo-uncapped-db7150d305764d4d887d69cd1c9697ab`.

- `result.json`, `accounting.json`: terminal result, usage, phase costs and probes.
- `worker-verified-grade.json`, `delegated-verified-grade.json`: scope and tests.
- `delegated/accept-final.txt`: Sol's explicit acceptance of the quote judgment.
- Sol session: `01a0c63c-ff45-78b1-843d-793941a431c5`.
- Kilo run: `20260922-001321-f79b10e7`; session: `ses_f39c10e98ffe46R5Hd3Bs10B0I`.

The Kilo run preserves its receipt, handoff, events, manifest and profile.
`analyze.py --uncapped` reproduces offline accounting, grades, byte comparison
and the quote probe against both the candidate and original reference.
