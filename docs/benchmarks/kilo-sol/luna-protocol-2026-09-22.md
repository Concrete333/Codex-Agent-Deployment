# Sol High with a Luna Max worker

One additional delegated arm on the same frozen six-adapter task. Reuse the
completed Sol High solo baseline and Sol/MiMo pair; do not pay to repeat them.
The new arm is Sol High preparation, one Luna Max Codex CLI worker, then resumed
Sol High acceptance and any local repair. Software owns waiting, not a model.

Reuse the exact source, 146 visible and 98 held-out cases, allowed edit paths,
assignment schema, coordinator model/effort, 30-minute stage timeouts and
independent grading. Do not expose prior solutions, findings, the malformed-CSV
post-hoc probe or held-out results to either model. Count all three stages,
including a failed worker attempt; no automatic model retries.

Required runtime differences from the MiMo arm:

- Sol reads the installed deployment skill and delegation guide rather than the
  Kilo skill. The chosen worker is explicit; no model-selection guide is loaded.
- Luna receives the fresh assignment through Codex, without Sol conversation
  history. Both Codex processes have other agents, plugins and skills disabled.
- Codex has no equivalent configured Kilo 30-step cap here. The worker's wall-time
  limit remains 30 minutes; do not claim matched iteration budgets.
- A separate pristine Git checkout uses `core.autocrlf=false`; source bytes are
  preserved. The host copies only allowed changes into Sol's checkout.
- Worker handoff and resumed acceptance explicitly use a result schema. This
  avoids inheriting the previous trial's preparation-contract response shape.

These are deployment-path comparisons, not isolated model substitutions.
Disclose the policy, tool, schema and iteration-limit differences. One new run
does not establish a general ranking or subscription-allowance saving.

`luna.py prepare` performs offline source-hash, checkout and reference checks.
`luna.py run` is the paid arm. The ignored `local-luna.json` points to retained
local evidence; final cost accounting must reconcile both Codex sessions and
must not add cumulative resumed usage twice.
