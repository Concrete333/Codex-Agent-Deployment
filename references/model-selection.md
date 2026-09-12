# Choose a worker and effort

Choose only Luna, Terra, Sol or Opus 5. Keep Astra-level work with the orchestrator. These are alternatives for bounded assignments, not an escalation ladder.

## Cost and acceptance

Use this guide after identifying work that delegation removes from the coordinator. Compare the complete attempt, including handoff, checking and likely repair, with local completion. Do not invent a precise saving without comparable accepted outcomes.

For scale, captured API-priced suite averages are Luna Max **$0.18**, Sol Low/Medium/High **$0.26/$0.50/$0.81**, Opus 5 Low **$1.10**, Terra Max **$1.40** and Sol Max **$1.99**. These indicate relative cost, not task quotes or subscription allowance rates. Lower effort can reduce generated tokens; it does not itself lower a model's per-token price. Include parent and worker context.

Match the worker to the uncertainty remaining: retrieval or a fixed transformation; local implementation judgment; or reasoning about unfamiliar behavior. Test code follows the same distinction. Coordinator reconstruction or repair can erase a worker's price advantage.

## Luna — extraction and pattern-following implementation

**ID:** `gpt-5.6-luna` · **Effort:** `max` only.

Use for bounded repository searches, caller maps, extracting supplied evidence, repetitive edits and small implementations following an established pattern. Supply search boundaries or the pattern, explicit behavior and objective checks.

Choose Luna over Terra or Opus when the work mostly finds or transforms information rather than making consequential implementation decisions. Its low cost matters when it removes substantial reading or repetitive work; do not delegate a trivial edit the coordinator can finish immediately.

Examples: reconcile callers for a known API rename, or extend a regression fixture with settled inputs and expected outputs. Discovering what unfamiliar behavior should be tested is not pattern-following work. If preparing a Luna assignment requires solving it, keep it local rather than writing a detailed solution for delegation.

## Terra — bounded native implementation

**ID:** `gpt-5.6-terra` · **Starting effort for repository implementation:** `max`.

Use for a settled feature or repair requiring local judgment beyond Luna's pattern-following scope: an endpoint using existing conventions, validation across a few files, or a regression-backed behavior change. Supply interfaces and failure cases; normally let the worker own the change, focused tests and corrections. Keep cross-cutting design decisions outside the assignment.

Choose Terra over Luna when locating the code is easy but implementing it needs connected reasoning. Choose it over Opus when native tools, retained context or avoiding Claude setup makes the whole attempt preferable. Do not assume Terra Max is cheaper than Opus Low on a completed task.

Lower Terra efforts are not the starting recommendation for autonomous repository coding. Use them only for a narrower assignment already shown adequate with reliable checks. Consider Sol for supplied analytical problems. If Terra would need extensive coordinator repair, keep the work local.

## Sol — bounded analysis, diagnosis and reasoning-heavy subproblems

**ID:** `gpt-5.6-sol`.

- **Low (`low`):** a narrow analytical or scientific Python problem with supplied background and executable checks.
- **Medium (`medium`):** multi-step derivation within that settled scope when Low lacks enough reasoning.
- **High (`high`):** bounded diagnosis, professional analysis or independent review with an explicit question, evidence and checking standard.
- **Max (`max`):** a specialist derivation or contained coding problem with a concrete extra reasoning need. Use only when the coordinator still saves work, not to replace an Astra worker.

Choose Sol over Luna for deriving or evaluating a solution rather than extracting or mechanically editing. Choose it over Terra for supplied scientific/analytical work. Terra Max or Opus Low are initial candidates when autonomous implementation is the main requirement; Sol Low/Medium are not interchangeable cheap general developers.

Sol High is a candidate for bounded review, not an interchangeable replacement for the coordinator. Use it to replace substantive checking only with evidence it detects the relevant error types; otherwise retain direct verification of unresolved requirements. Assign review and correction verification together. Do not promote to Max merely because it is reviewing.

For diagnosis, assign a specific failure and require a reproduction or discriminating check. Sol High can design tests for a named risk; derive expected behavior from the contract, not the implementation. “Find whatever is wrong with this system” stays local.

## Opus 5 — implementation through Claude

**ID:** `claude-opus-5` · requires authorized Claude CLI and account use.

- **Low (`low`):** start here for bounded repository implementation requiring navigation and local decisions. Supply interfaces and required behavior; normally assign the implementation, regression checks and corrections together.
- **Medium/High (`medium`/`high`):** retain a useful owner when a concrete remaining reasoning need justifies additional cost.
- **X-High/Max (`xhigh`/`max`):** only for a bounded specialist requirement with evidence that extra effort helps. Do not use them to outsource the orchestrator's hard work.

Choose Opus over Luna for independent implementation judgment; over low/medium Sol for repository work rather than a supplied derivation. Choose it over Terra when Claude access/preferences, an established session or comparable accepted outcomes justify the route. Opus Low is a lower-cost initial candidate than Terra Max on the captured scale, but startup, inherited context and review can erase that advantage.

Avoid a fresh Claude session for a tiny change. Raise effort for a specific unresolved limitation, not because the project is important. Architecture and difficult coupled reasoning return to the orchestrator.
