# Waiting-only probe — 10 September 2026

The native completion wait worked in one bounded test on Codex CLI 0.153.4.
Astra High spawned one Luna Max worker without inherited history, called
`collaboration.wait_agent` once, and resumed when the worker finished. The
parent made no clock sleeps, status polls or repeated model requests while
inside that wait.

The worker ran a forty-second dummy command and returned `WAIT_PROBE_DONE`.
The wait requested 1,500,000 ms, returned after approximately 50.13 seconds
with `timed_out: false`, and the whole test took 68.23 seconds. The parent had
three model responses: dispatch, wait, final report. Luna also had three;
its shell command yielded once and required one completion collection.

This verifies an early completion wake in this CLI, not twenty-five minutes
of idle suspension, user-input interruption, the desktop runtime, or compliance
under every host's responsiveness limits. A skill cannot override those limits.
The previous coding run used clock sleeps; this probe establishes a working
native wait path, not why that earlier run chose differently or how much a
full rerun would save.

## Scope and cost

The probe reuses C2's trusted command/configuration manifest, including disabled
skill discovery and the 25-minute wait settings. It supplies a short waiting-only
prompt, not the full deployment skill, project or benchmark. It stops without
spawning if the completion wait is unavailable or disallowed. There is one
permitted worker and a three-minute process-tree safety limit. No user settings,
billing settings or credentials were changed.

| Agent | Input | Cached input, included | Output | API-equivalent estimate |
| --- | ---: | ---: | ---: | ---: |
| Astra High parent | 36,748 | 23,936 | 381 | $0.171106 |
| Luna Max worker | 42,438 | 13,056 | 431 | $0.006655 |
| Team | 79,186 | 36,992 | 812 | $0.177761 |

The final per-thread counters include all captured responses, with no cache
writes. Reasoning is already included in output. Rates per million tokens:
Astra $10 input/$1 cached/$50 output, matching the earlier trial basis;
Luna $0.20/$0.02/$1.20, checked against the
[official model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).
These are estimates, not subscription charges. This supervising conversation
and preparation are outside the probe totals.

Official [subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
describes waiting and orchestration; the exact early-wake behavior above is
established by local tool calls and responses, not inferred from that page.

## Reproduce only with spending authorized

```powershell
python -B -X utf8 docs/benchmarks/waiting/probe.py <trusted-local-C2-manifest.json>
```

This executes the command in the manifest; never supply an untrusted manifest.
Raw receipts stay in the printed temporary directory. Do not run this probe
on every skill invocation: reuse confirmed runtime behavior until relevant
runtime/configuration changes.

Local receipt directory: `agent-deployment-waiting-ozua6gin` under system temp.
Parent: `01a08897-ba9c-7930-8369-bd640a51cd0c`.
Worker: `01a08897-f05a-7023-bfe1-76c3c9b3f992`.
