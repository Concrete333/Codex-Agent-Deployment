# MiMo single-worker retry — 22 September 2026

One user-authorized retry of the frozen inventory implementation task, following
the upstream 503 timeout in the external-worker comparison. No demonstrated local
fix explains that timeout; this tests whether the same route can now complete.

- Kilo 7.7.7; `kilo/xiaomi/mimo-v2.6-pro`, variant `thinking` (highest exposed).
- Same task contract and byte-identical committed starter as the external-worker
  comparison, in a fresh checkout; no prior implementation or failed-session resume.
- Normal implementation tools, no step cap, 65,536 per-response output ceiling,
  1,800-second worker timeout. No global configuration changes.
- One worker attempt only; no automatic relaunch or paid Astra fallback session.
- The existing supervisor saves the terminal receipt and attempts one completion
  notification. Parent review waits for that event, without polling.
- On completion, verify ownership, scope and handoff; inspect implementation and
  run the unchanged 27-method independent grader before accepting any result.
- Retain failure evidence and reported cost; unknown failed-request usage remains
  unknown. Coordinator analysis is separate from worker cost. This is a worker
  reliability retry, not another priced end-to-end comparison.

Baseline: [external-worker results](external-workers-results-2026-09-22.md).

## Result

Worker run `20260922-122840-44d18e78` exited 1 after **640.03 seconds**.
MiMo completed two reading/tool responses, then returned:

```text
503: The upstream provider timed out while sending the response.
type: timeout
request id: lhr1:lhr1::wfhs6-1790076558415-9cd06edee822
```

No implementation, added tests or handoff was produced. Git status was clean and
all tracked candidate files matched the frozen starter byte-for-byte. There was
no candidate to grade or accept; the independent grader was not rerun against
the unchanged starter. No repair, further worker or paid fallback was launched.

The resolved profile confirmed MiMo with variant `thinking`, without a step cap.
The task-contract hash matched the prior attempt. The last completed response
ended with `tool-calls`, not `length`. The error event followed that response by
600.822 seconds, before the local 1,800-second timeout. This repeats the earlier
upstream-timeout failure; it does not identify whether Kilo's gateway or the
upstream service imposed the timeout, or why generation failed to finish.

Two unique completed-step costs sum to **$0.0076103724**. Usage for the failed
request is unknown, so this is incomplete worker accounting, not total cost.
Completed steps recorded 15,842 input tokens, 13,184 cache-read tokens, 742 output
tokens and 30 reasoning tokens under Kilo's event schema. Coordinator inspection
is excluded. Session: `ses_f371fdfc3ffebGAhsnHMS7nF9v`.

The supervisor recorded confirmed termination and no ownership issue. Both
recorded processes were absent and the ownership lock was removed. One completion
message was queued and resumed this task; no model-driven polling was needed.
The run directory retains the receipt, manifest, resolved profile, events and
stderr. This result supports avoiding this route pending diagnosis, not a claim
that MiMo cannot implement the component.
