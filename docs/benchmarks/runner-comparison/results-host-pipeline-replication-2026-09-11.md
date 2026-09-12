# Host pipeline replication: accepted without manual recovery

The repaired pipeline completed automatically: Luna Max implementation, deterministic handoff/file/check gates, then fresh Astra High acceptance with local corrections permitted. **Captured API-equivalent cost was $0.894435**, with all 146 visible cases, 98 held-out cases and three new regression tests passing after acceptance. No worker retry or manual infrastructure recovery was needed.

| Run | Luna Max | Astra High acceptance, corrections and rechecking | Total |
| --- | ---: | ---: | ---: |
| Saved native delegation | $0.110186 | $1.049822 | $1.160008 |
| First accepted host pipeline, after offline recovery | $0.070984 | $0.929744 | $1.000728 |
| Unchanged replication, attempt 03 | $0.136257 | $0.758178 | $0.894435 |

This replication costs 22.9% less than the single saved native-delegation run. The two accepted host runs average $0.947582. Total captured host-pipeline model spending across the earlier timeout and both accepted runs is $1.980020; the interrupted attempt may omit in-flight usage. These are descriptive results, not a statistically established saving. This comparison does not measure solo work or no-skill delegation.

## What stayed fixed

Preparation started from fresh stubs and asserted both model prompts and the acceptance command matched attempt 02 after checkout-path substitution. The source fixture, model-facing policy snapshot, checks, ownership and acceptance requirements were unchanged. Luna retained Max effort and a 1,800-second safety limit; Astra retained High effort and 1,200 seconds for acceptance. The repaired sandbox hashing path was already present before dispatch.

No judgment-call field, read-only reviewer restriction, worker correction round or new probe was added to the frozen trial. Neither participant received earlier submissions, review findings, the XML adjudication discussion or external grading results. A durable start marker prevents an automatic paid rerun. Research supervision, harness work and external grading remain outside measured model cost, as in the earlier comparisons.

## Execution and verification

- Luna completed in 1,235.848 seconds, returned a complete handoff and passed the runner's final visible check. The private external grader also passed all 244 frozen cases before acceptance. No added discoverable tests existed at this point.
- The driver verified handoff-listed and required files, protected evidence and declared checks, then started Astra. No benchmark coordinator existed while Luna worked.
- Astra inspected the six adapters and identified malformed CSV quote handling. Its recorded pre-correction probes show both CSV formats accepting `bad"quote` as an unquoted memo. It modified only the shared parsing helper and added `test_csv_quoting.py`.
- The three new tests cover malformed quotes, valid quoted memo preservation and empty/escaped-quote fields. The final external grader passed all 244 frozen cases plus those tests. All nine runner-protected files remain unchanged.
- The same three tests were run read-only against the reference and saved native/live-software baselines; all passed. This is a reference-confirmed CSV defect and correction, not the disputed XML case from the earlier run. These new tests are post-hoc review evidence, not independent held-out additions to the frozen suite.
- Astra made several unsuccessful relative-path reads from `C:\` and one denied directory-change attempt before recovering with usable paths. The recorded failed reads returned no source contents. These self-corrected tool errors and their model costs remain included; "without manual recovery" does not mean error-free execution.
- The complete workflow took 1,381.643 seconds. Worker and acceptance processes stopped, and no active runner claim remained.

The earlier report was corrected separately: its CSV finding is reference-confirmed; its CDATA/DOCTYPE change remains an open reference/contract discrepancy. No XML accuracy gain is counted here, and those reporting changes were not fed into this replication.

## Recorded usage

| Configuration | Responses | Input | Cached input | Output | Reasoning output, included in output |
| --- | ---: | ---: | ---: | ---: | ---: |
| Luna Max | 29 | 1,729,828 | 1,560,832 | 59,368 | 26,256 |
| Astra High | 12 | 261,624 | 224,768 | 3,297 | 474 |

Models and efforts were confirmed from rollout turn contexts, and own-thread response usage reconciles to recorded totals. Acceptance made no delegation or worker-wait calls. Frozen historical API-equivalent rates are used; these are not actual bills or Codex allowance measurements.

Acceptance/corrections were 84.8% of cost, while Luna was 15.2%—the worker was not under 10% this time. Luna cost nearly twice its preceding run; the acceptance session cost less. The total saving therefore cannot be attributed to a deterministic fixed worker cost or entirely to waiting. Astra's figure remains a combined verification-and-implementation cost, not directly comparable to a read-only reviewer price.

## Takeaway

The host-execution/fresh-acceptance architecture now has one uninterrupted successful run, alongside the earlier accepted run requiring offline repair. Both captured totals are below the saved native baseline. The recurring CSV miss also shows why passing the frozen suite alone is insufficient for acceptance.

Do not change routing or claim general savings from these two samples against one native sample on a repeatedly used fixture. The next separately authorized reviewer experiment can use the shared planted defects for a cross-model comparison. Those defects are known to the teams, so that experiment must not be described as unseen validation. Changes to handoff fields, reviewer write permissions or correction routing should be separate experiments.

## Evidence

`host_pipeline.py prepare|run|summarize --attempt 03` is the guarded entry point. The ignored `local-fixture.json` locates `host-pipeline-03/`, containing frozen hashes/prompts/commands, the worker receipt path, before/after grades, event logs, reconciled accounting and `postflight.json`. `audit_acceptance.py --attempt 03` runs only offline checks. All earlier evidence is retained.

Worker: `01a09107-02a9-7da2-bdb5-33bab60138fe`. Acceptance: `01a09119-ed7e-7901-b38e-33348c2f4557`.
