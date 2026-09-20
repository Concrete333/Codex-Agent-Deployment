# Wait for scripts and workers

Use this for an authorized long-running script, test suite, build, database job or foreground worker CLI. Keep short commands direct. Prefer an existing supported completion notification or event-driven wait within tool and responsiveness limits; do not add a model just to watch a process.

## Choose a completion route

- Before a new job, establish its allowed side effects, result location, success checks and work timeout. Detach only when it can safely survive the turn ending without interactive input.
- Choose and set up the completion route before launching full suites or other expected long jobs, including verification at the end of a coding task. A shell session ID or saved log alone does not establish automatic wake-up. Check native completion support or run the helper's `check` command below; reuse a verified result until the environment changes.
- For a job already running, use its existing completion mechanism. Do not restart it, launch a duplicate or pass its launcher to the helper. If it has no supported completion route, use the manual fallback below.
- If native completion already wakes the parent, do not add a second callback. For remote jobs such as CI, an authorized bounded watcher may wait in software; keep routine status checks out of model turns.
- Use `scripts/completion_notify.py` when the host can run the command and `codex queue` for the current task. It waits in software, saves a process receipt, then submits one follow-up. Do not queue the follow-up before completion.
- The command must enforce its own work timeout and child-process cleanup. The helper adds neither. If those controls are missing, establish an appropriate bounded execution method before detaching. Retain meaningful failure/progress checkpoints when the task requires intervention; do not replace them with repetitive model checks.

## Start with completion notification

Requires Python 3.10+ and a native Codex executable supporting `queue --thread --message`. Confirm the current task UUID, for example from `CODEX_THREAD_ID`; do not guess a session name. Keep supervisor files and private state outside the job's write scope. Do not bypass sandbox or approval requirements to reach the host.

Locate the native executable (`Get-Command codex.exe` on Windows), then preflight without starting a job:

```powershell
python C:/path/to/agent-deployment/scripts/completion_notify.py check --codex C:/path/to/codex.exe --thread CURRENT-TASK-UUID
```

If supported, launch through `start` below rather than starting the command separately and planning to add notification later. A successful check confirms CLI support, not guaranteed delivery.

Create a UTF-8 JSON request with absolute paths and a trusted argument array:

```json
{
  "codex": "C:/path/to/codex.exe",
  "thread": "CURRENT-TASK-UUID",
  "cwd": "C:/work/project",
  "argv": ["C:/Python313/python.exe", "C:/work/project/scripts/bounded_check.py"]
}
```

Replace `argv` with the actual authorized foreground command. The example assumes that script owns its timeout and cleanup. Do not use a launcher that returns while its children keep working. An optional `receipt` field links a result file produced by the command; it is not automatically validated.

```powershell
python C:/path/to/agent-deployment/scripts/completion_notify.py start --request C:/work/private/notify.json --run-dir C:/work/private/notifications/unique-attempt
```

Use absolute native executable paths on all platforms; Windows requires `.exe`, not shell shims. Start checks CLI support, requires a new run directory and returns immediately. Do independent work or end the turn. Tell the user what is running, where results will be saved, what verification remains and a rough remaining time from existing evidence (or unknown). Say notification is armed, not guaranteed; keep the host available.

## On completion

The supervisor retains `stdout.log` and `stderr.log`, writes `process.json`, then attempts one notification on success or failure. `process.notification.json` records delivery. Queued means submission accepted, not successful work. The notification command returns nonzero for failed or uncertain delivery. An existing delivery record suppresses another attempt; do not automatically retry uncertainty or rerun work to repair delivery.

On wake-up, correlate the event with its run directory or job ID and handle each terminal result once, even if native and queued events both arrive. Honor newer stop, pause or scope changes before continuing. Inspect the receipt and relevant results; confirm execution and ownership are resolved before dependent work. Verify the task's actual outcome; process exit, worker claims and notification delivery are not acceptance.

After confirmed termination, a verified mechanical fix permits a safe rerun within existing scope and budget without renewed permission. Preserve failure evidence and announce the retry. Reassess repeated failures; ask before material extra spending or actions outside existing authority. Never retry with uncertain ownership or duplicate side effects.

## Without a usable notification route

State the concrete limitation: unavailable CLI support, missing target identity, host permissions, unsafe detachment, or an already-running job with no attachable completion route. Do not infer unavailability from a command still running or a tool wait timing out. If setup was missed, say so; do not restart existing work to repair the omission.

If independent work is exhausted, leave only safely persistent work running. State its result location, pending verification and rough remaining time or unknown. Say: "I'm stopping polling. Please check back with me to inspect the result and continue; I won't automatically resume." End the turn. If it cannot safely survive, explain the limitation instead.

On return, inspect once: verify and continue if complete; otherwise report briefly and stop again. Do not repeatedly inspect unchanged logs, sleep and check, cancel or replace a job because a wait timed out, or create an automation unless requested. Preserve safety timeouts and higher-priority responsiveness requirements.
