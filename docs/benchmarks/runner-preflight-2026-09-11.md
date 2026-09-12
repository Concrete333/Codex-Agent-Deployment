# Native versus software runner: preflight blocked

The requested paired trial did not reach model inference. No paid participant calls, implementations or accuracy/cost results were produced.

## Intended comparison

Use the existing version-two six-adapter fixture: 146 visible and 98 held-out cases, identical starting files and acceptance criteria. Both arms use Astra High as coordinator and exactly one Luna Max worker. Compare native delegation with the new software runner owning dispatch, completion bookkeeping and the same final objective checks. Keep substantive review with the coordinator in both arms.

## Observed preflight results

Installed native Codex CLI: 0.153.4. Commands used the existing elevated Windows sandbox and the frozen reference checkout; no settings, credentials or billing were changed.

| Check | Result |
| --- | --- |
| Python command inside the read-only sandbox | `sandbox-ready`, exit 0 |
| Native Codex `login status` on the authenticated host | `Logged in using ChatGPT` |
| The same executable's `login status` inside `:read-only` sandbox | `Not logged in`, exit 1 |
| The same executable's `login status` inside `:workspace` sandbox | `Not logged in` |

The workspace check used this command shape:

```powershell
codex.exe sandbox -P ':workspace' -C <frozen-reference-checkout> -c 'windows.sandbox="elevated"' -- <same-native-codex.exe> login status
```

This is a launch-context/authentication blocker for the planned nested CLI route. It does not establish whether the login is absent, inaccessible or resolved differently under the sandbox identity. It does not establish the cause of the separately reported Node/module warning, which was not pursued.

## Consequence

The software runner requires a recognized ChatGPT login before starting a Codex worker. That guard would block when called from this sandboxed coordinator shell. Running the native arm anyway would spend on a pair whose runner arm cannot execute. Both paid arms were therefore withheld.

The earlier 57 offline tests and host-side authentication checks did not cover authentication from a sandboxed caller. This preflight exposes that integration gap; it is not an accuracy failure or evidence about orchestration cost.

The runner can be launched from the authenticated host, but a sandboxed coordinator needs an explicit, narrow host-side dispatch mechanism to use it. Do not copy credentials into the sandbox or disable sandboxing to force the test through. Qualify the chosen launch path before freezing and running the pair. Direct host execution alone would be a runtime smoke test, not the promised matched coordinator-cost comparison.
