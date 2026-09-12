# Recovered software arm — 11 September 2026

**The repaired route works, but this run cost 89.6% more than native delegation. Both passed the same 244 cases.**

## Comparison

| Measure | Saved native baseline | Recovered software arm |
| --- | ---: | ---: |
| Coordinator | Astra High | Astra High |
| Worker | One Luna Max | One Luna Max |
| Visible cases | 146/146 | 146/146 |
| Held-out cases | 98/98 | 98/98 |
| Coordinator code corrections | 0 | 0 |
| Coordinator cost | $1.049822 | $2.102332 |
| Worker cost | $0.11018636 | $0.09702320 |
| Accepted workflow cost | **$1.16000836** | **$2.19935520** |
| Coordinator responses | 16 | 54 |
| Worker responses | 46 | 29 |
| Complete arm seconds | 921.084 | 1,067.368 |

Costs are API-equivalent estimates using the original experiment's frozen rates, not subscription allowance or charges. Research preparation/supervision and external evaluation are excluded. All participant response records reconcile with their own-thread usage totals; actual model/effort contexts match the requested configurations.

The prior software launch failure cost $0.446918. Including it, total software spending was **$2.64627320**, 128.1% above the native baseline. The fresh successful arm and failure-inclusive total are separate measures. Two subsequent fake-worker preflights used no model calls; the first failed and the second passed.

## Where the additional cost occurred

Luna cost 11.9% less in the recovered software arm. Astra's cost roughly doubled. The largest recorded increase occurred while the worker was running:

| Coordinator phase | Native cost | Software cost | Native responses | Software responses |
| --- | ---: | ---: | ---: | ---: |
| Before worker execution | $0.459560 | $0.281326 | 8 | 6 |
| While worker was active | **$0.038052** | **$1.203016** | **1** | **41** |
| After worker completion | $0.552210 | $0.617990 | 7 | 7 |

The native coordinator used one native completion wait. The software coordinator used 27 outer `wait` calls: one requested a 1-second yield and 26 requested 30 seconds. Thirteen returned only a still-running marker with no new output. These wrap the shell process wait; they are not extra worker attempts. During worker execution, the software coordinator accumulated 801,929 input tokens, including 769,536 cached, versus 27,983 input tokens in the native arm.

The worker's Python process remained blocked in software, but the surrounding shell/tool wait layer repeatedly resumed the coordinator model. Moving the internal wait into Python did not remove the expensive outer wake-ups. The recorded increase in the while-worker phase was $1.164964, larger than the $1.03934684 net workflow increase because other categories partly offset it.

These timestamp bins are descriptive, not a causal estimate of precisely how much a different wait implementation would save. They include any commentary and tool handling in that interval. The software worker also ran longer: 883.096 seconds versus 725.849 seconds by task-event timestamps. Both remained within the software arm's planned 900-second worker limit, and neither coordinator reached the 1,200-second limit.

## Accuracy and review

Both results passed protected-file/scope grading, the visible suite and the held-out suite. Neither added discoverable test files. Each coordinator reviewed all six adapters and the shared parser without modifying the implementation after handoff. Native reported 113 inline review assertions; software reported 2,318. Those counts represent different generated probes, not comparable coverage scores. Post-completion coordinator costs were much closer than their waiting costs.

The research audit inspected the recovered implementation after completion and found no additional material contract defect. This is bounded evidence, not proof of correctness for every input. No held-out failures or reference solutions were fed back to either participant.

The software coordinator reported an unintended outside-checkout filename enumeration after a failed PowerShell directory change. It said it disregarded the listing. The listing and recovery remain in its transcript and cost; this is an instruction-constrained isolation deviation, not an intentionally supplied task hint. It further limits causal comparison. Native also encountered a working-directory mismatch, as recorded in the original results.

## What was fixed

The original paid software arm failed because its copied temporary host script was unreadable by the sandbox. The recovery uses the canonical repo runtime path, with hashes pinned before execution. The runner and Claude-helper bytes still match the original snapshot; the policy, assignment, model settings, task, deadlines and grader were preserved apart from fresh paths and request identity.

The first recovery preflight then found a second issue: the client could read the authorized endpoints but could not stat an intermediate parent directory. The host now retains full ancestry checks before issuing a private ticket; the client checks endpoint identity/overlap without repeating inaccessible ancestor inspection. No ACLs, credentials or global configuration were changed.

The full fake-worker exchange qualified the exact sandbox, interpreter, shell, client script, ticket and receipt route before inference. It also checked private-state write denial and repeated receipt retrieval without redispatch. The offline suite now passes **82 tests**, including a regression that the host still refuses an uninspectable boundary. The repaired host script is synced to the installed skill.

## Takeaway

Keep native delegation as the default in this runtime. The software route is functionally qualified but has not achieved its cost objective. The next engineering question is how to deliver completion through the outer shell/tool boundary without repeated model re-entry—not another model substitution or reduced acceptance coverage.

This was one recovered software arm compared with a saved native baseline, not a new uninterrupted randomized pair. Cache state, sampling, runtime-added worker context, worker duration and the directory-listing deviation were not controlled. Replication would be needed before claiming a general cost effect; nothing here shows that software bookkeeping is inherently more expensive in every host.

## Evidence

- [Original failed pair](results-2026-09-11.md), [protocol](README.md), [recovery harness](recover_software.py), [phase analysis](analyze_waits.py).
- Local root: `C:/Users/cwbec/AppData/Local/Temp/agent-deployment-runner-pair-_jkwg0ue/software-recovery-02`.
- Main records: `manifest.json`, preflight JSON files, `result.json`, `grade.json`, `accounting.json`, `phase-accounting.json`, `events.jsonl` and `stderr.log`.
- Private worker receipt: `C:/Users/cwbec/AppData/Local/AgentDeployment/agent-deployment-runner-pair-_jkwg0ue/adapter-software-recovery-02/receipt.json`, also exposed through Windows' packaged-app LocalCache alias.
- Coordinator session: `01a09097-1d18-7553-9053-62586f5a025f`; worker session: `01a09097-bccb-7801-be5f-6507b84ff8ae`.

The earlier failed paid arm and failed offline preflight remain intact. No further paid retry was launched. Raw sessions and private receipts remain outside Git.
