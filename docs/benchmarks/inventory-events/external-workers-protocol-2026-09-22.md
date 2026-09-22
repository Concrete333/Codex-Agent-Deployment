# External workers with Astra acceptance

## Question and fixed conditions

Compare one implementation attempt each from MiMo-V2.6-Pro, GLM 5.3 Flash and
DeepSeek V4.1 Flash through Kilo, followed by Astra High acceptance. Reuse the
22 September inventory starter, contract, acceptance prompt and 27-method grader.
One method includes 80 lifecycle scenarios; these are not separate test methods.
Requalify the correct controls and nine defective variants before inference.

| Worker route | Highest exposed Kilo variant | Catalogue reasoning setting |
|---|---|---|
| `kilo/xiaomi/mimo-v2.6-pro` | `thinking` | enabled, high |
| `kilo/z-ai/glm-5.3-flash` | `max` | enabled, max |
| `kilo/deepseek/deepseek-v4.1-flash` | `max` | enabled, max |

Save current catalogue entries and resolved agent profiles before launch. These
verify requested routing/configuration, not that an upstream provider honors
every setting internally. Do not invent a MiMo max variant or substitute models.
DeepSeek's [official thinking guide](https://api-docs.deepseek.com/guides/thinking_mode/)
also documents max; high and xhigh are not equivalent to max on that API.

All workers have normal implementation tools, no iteration cap, the same
65,536-token response ceiling as the preceding MiMo trial, and a 30-minute
process-tree timeout. Keep compaction enabled and global configuration unchanged.
The response ceiling is separate from reasoning effort and is not each model's
maximum advertised output size. No automatic paid retries. Up to six task
sessions: three workers and three fresh Astra High acceptance/fallback sessions.

Use independent checkouts. Reuse `three_arm.run_arm` for ownership, scope,
grading and acceptance. Astra can correct or finish partial work; record that
cost as correction/fallback rather than attributing the final pass to the worker.
Do not reveal independent grades to task models. Software handles waiting and
queues one result notification for the batch; no model polling.

The prior solo Astra and Luna results are historical comparators, not fresh
controls. Kilo is now 7.7.7 rather than 7.7.6. Record this confound: a successful
MiMo retry cannot by itself identify whether a client update or provider state
resolved the earlier failure. Keep the previously frozen acceptance policy for
comparison; this is not a trial of the newly edited skill text.

Preflight stopped on the installed 7.7.7 version before paid calls. Implementation,
exploration and review profiles then passed no-inference checks; all 53 wrapper
tests passed. The version pin was updated in the repository and installed copy.
The trial's six offline harness/configuration tests passed. No provider call was
needed for these checks. The abandoned preflight directory remains on disk.

## MiMo failure investigation before the run

The earlier adapter run ended with `finish_reason=length` after roughly 32k
reasoning tokens. Kilo documents a default 32,000-token output ceiling and its
[per-process override](https://kilo.ai/docs/customize/context/context-condensing#cli).
That ceiling was a runtime constraint, distinct from the removed 30-step cap.

The subsequent inventory run `20260922-093625-0207351e` requested 65,536 output
tokens with no step cap. It completed two tool-reading responses and then failed:

```json
{"name":"APIError","data":{"message":"Stream error occurred","isRetryable":false,"responseBody":"{\"code\":\"error\",\"message\":\"Stream error occurred\",\"name\":\"AI_InvalidResponseDataError\"}"}}
```

Kilo exited 1 after 594.66 seconds, before the 30-minute timeout. It produced no
edits or handoff. The last completed response ended with `tool-calls`, not
`length`. The resolved profile confirms the requested MiMo model, thinking
variant, uncapped steps and normal implementation permissions. Our handoff
validation ran after this error; it did not cause the failed model stream.

The retained CLI log supplies no raw failing response or provider request ID.
The failure is at the API/stream boundary, but available evidence cannot isolate
Kilo's gateway, upstream provider, model-generated protocol content or an
interaction with the output setting. No completed usage record exists for the
failed request. Do not call this a proven wrapper bug, model reasoning failure,
or fixed defect. This authorized new attempt is diagnostic replication.

## Accounting and acceptance

Preserve each worker's pre-review files, handoff, checks, errors and usage, plus
the final Astra candidate and rollout. Include failed attempts and Astra repair
in cost through acceptance. Missing provider usage remains unknown. Separate
worker correctness from final pipeline correctness and report changed files.
Preparation and this supervising conversation remain outside execution totals.
API-equivalent estimates and Kilo reported costs are not subscription bills.
One run per model does not establish average savings or a reliability ranking.
