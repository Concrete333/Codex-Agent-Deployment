# Choose the model, effort and acceptance check

Choose for the hardest requirement left in the worker's assignment, not the complexity of the original project or its job title. A large input may need cheap extraction; a ten-line change may need difficult reasoning. These recommendations are starting points, not a mandatory sequence. Keep useful existing worker context when a handoff would cost more than it saves.

## Define an accepted result first

An accepted result meets the assigned requirements, with evidence covering the important failure modes and unresolved issues disclosed. A successful process exit or a worker's “complete” is insufficient.

| Assignment | Evidence needed for acceptance |
| --- | --- |
| Extraction or source mapping | Exact source locations, the search scope, reconciled counts or coverage checks, and explicit gaps. Spot checks alone do not prove completeness. |
| Repetitive edits | The intended set changed, unintended locations stayed unchanged, and relevant syntax/type/behavior checks pass. |
| Diagnosis | A reproduction or discriminating check supports the cause; competing explanations and remaining uncertainty are addressed. |
| Implementation | Checks exercise the requested behavior and relevant failure cases; affected interactions work after integration. |
| Review or professional deliverable | Requirements/rubric checked against artifacts and sources; findings or claims have evidence. A plausible summary or no reported defects is not proof. |

Use deterministic tools where they can do the work. Settle consequential decisions before delegating their implementation; choose for the judgment still required. A precise specification can make work suitable for a cheaper model, but cannot remove all implementation difficulty. If preparation and checking would require solving the whole problem again, keep one capable owner. A stronger worker still needs checks.

## Cost reference: compare the whole attempt

Costs are API-priced benchmark averages (2026-09-08) for relative comparison, not assignment quotes or subscription usage. Prefer measured total cost on comparable work.

Count worker input/cache use and output, coordinator work, verification, retries and integration. Many cheap tokens can cost less than fewer expensive ones. Time saved is not a selection benefit for this skill.

## Luna: economical work on supplied evidence

**ID:** `gpt-5.6-luna` · **Max:** `max`, **$0.18**

Choose Luna for bounded extraction, finding callers, mapping a defined subsystem, or repeating an unambiguous edit with directly checkable output. Give it a question and search boundaries, not “understand the whole project.”

Luna can also implement a small, fully specified change when it follows an established pattern, leaves little consequential judgment and has a dependable checker. For example, add a validator using a named existing pattern, explicit valid/invalid cases and unchanged error behavior. If choosing the behavior or ensuring cross-module correctness remains the hard part, prefer Astra. Do not exclude Luna just because the assignment writes code, or assume every implementation can be made cheap by adding more instructions.

**Why Luna over Opus?** Opus 5 Low costs roughly six times as much on this scale. Use Luna when the work is locating evidence or following a fixed transformation; prefer a stronger worker for uncertain design, open-ended diagnosis or synthesis requiring independent judgment.

Luna uses Max. Effort does not replace missing evidence or a clear assignment. After one substantive non-trivial failed assignment, preserve the evidence and escalate; do not buy repeated Luna attempts.

## Sol: bounded analytical and scientific reasoning

**ID:** `gpt-5.6-sol` · **Low $0.26**, **Medium $0.50**, **High $0.81**, **Max $1.99**; effort values `low`, `medium`, `high`, `max`.

- **Low:** candidate for a narrow scientific Python subproblem with supplied background and executable checks.
- **Medium:** candidate when that bounded problem needs more reasoning. Its scientific-code results are close to High at materially lower cost.
- **High:** candidate for bounded professional analysis with an explicit deliverable rubric.
- **Max:** a specialist option for research-level physics or demanding professional work. For difficult repository coding, prefer Astra rather than automatically raising Sol's effort.

**Why Sol over Luna?** The work requires deriving a solution, not mainly finding or transforming supplied evidence, and a focused check can assess it.

**Why Sol over Opus?** Sol Low/Medium are lower-cost starting candidates for scientific Python functions with supplied background and executable checks. Prefer Astra or Opus when the assignment instead requires autonomous repository investigation and implementation.

## Astra: implementation and repository problem-solving

**ID:** `gpt-6-astra`

| Effort | Relative cost | When to choose it |
| --- | ---: | --- |
| Light (`low`) | $0.82 | Specified implementation or bounded diagnosis: behavior/interfaces are clear and meaningful regression checks are available. |
| Medium (`medium`) | $1.54 | Multi-step but well-specified work with strong checks when Light lacks sufficient reasoning; retain it where comparable work meets the standard instead of raising effort automatically. |
| High (`high`) | $1.72 | Uncertain causes, interacting modules, migrations or subtle correctness review. A candidate to start with when missed defects are consequential and checks are weak. |
| X-High (`xhigh`) | $2.31 | Particularly difficult repository reasoning where additional effort has a concrete purpose, such as unresolved interacting failure paths. Can be chosen directly. |
| Max (`max`) | $3.26 | A specific unmet reasoning/quality requirement or explicit user choice, not the default for “hard.” |

**Why Astra over Sol or Opus for general coding?** Start with Astra Light for repository implementation: it combines stronger general coding capability with cost close to Sol High and below Opus Low. Use Sol for supplied scientific subproblems, or Opus when the Claude route has a concrete advantage.

**Why High rather than Medium?** High's additional reasoning is worth considering for difficult correctness work at about 12% extra cost. Keep Medium when already adequate. X-High adds about 34% over High; Max adds another 41%. Require a specific unresolved reasoning need for those premiums; do not traverse the settings automatically.

Use Light/High for source-grounded factual work; require supporting sources. For review, select effort by the reasoning required. The coordinator retains final acceptance at its existing effort.

## Opus: Claude-based implementation when that route has value

**ID:** `claude-opus-5` · **Low $1.10**, **Medium $2.19**, **High $3.61**, **Max $5.86**; use corresponding lowercase effort values.

**Low** is a candidate for bounded implementation when Claude use is required/preferred. Choose it over Luna or low/medium Sol when the worker must navigate the repository and make local implementation decisions rather than follow a fixed transformation or solve a supplied scientific subproblem.

**Medium/High** can retain an effective Claude implementation owner when more reasoning is needed. **Max** is a specialist option for demanding professional/analyst work, not an automatic coding upgrade.

**Why Opus over Sol?** Autonomous implementation rather than a supplied scientific subproblem, authorized Claude-specific access/preferences, or valuable existing session context. **Why not always Opus?** With both providers equally usable, Astra is the stronger initial cost candidate for ordinary coding. Opus needs a task or workflow reason; neither its name nor lower token prices establish lower completed-task cost.

## Fable: pay for a specific specialist requirement

**ID:** `claude-fable-5-1` · **Low $2.37**, **Medium $2.98**, **High $3.91**, **X-High $5.98**, **Max $7.63**; efforts `low`, `medium`, `high`, `xhigh`, `max`.

Choose Fable when demanding scientific coding, difficult knowledge questions or complex professional deliverables exceed the required quality attainable with cheaper candidates. Its strengths are not a reason to use it for every difficult repository task.

- **Low/Medium:** options for bounded professional work already shown adequate at that effort; do not start High merely because the model is Fable.
- **High:** initial candidate for demanding scientific/professional work needing its strengths.
- **X-High:** consider when the extra scientific or analytical capability is needed. At about 2.6 times Astra X-High's cost, choose it for a specialist need, not a general coding upgrade.
- **Max:** reserve for a specific scientific or analytical quality gap that justifies about 28% extra cost over X-High.

**Why Fable over Astra, Sol or Opus?** A specialist quality requirement the cheaper candidate does not meet, or relevant local evidence—not provider diversity. Verify material claims against sources and the deliverable against its rubric. Where Opus already meets the standard, retain it.

## Make the choice and bound the attempt

State a short dispatch reason: “Luna Max: source extraction with count reconciliation,” or “Astra High: cross-module retry behavior; regression and integration checks.” Include the acceptance check and work budget in the assignment.

Use a cheaper first attempt only when failures are reliably detectable and its expected cost **plus extra checking/handoff and likely escalation** is below starting stronger. Without comparable task outcomes, use these recommendations provisionally and bound the attempt.

On failure, fix missing information, environment or requirements first. For a reasoning limitation, select a suitable stronger effort/model directly and preserve useful work. Do not repeat an unchanged approach or create parallel reasoning workers just to spend more attempts.

Other models can be justified by explicit user choice, account constraints or relevant task-specific evidence; this is not a whitelist. Confirm supported model/effort controls. Use native tools for GPT; read [claude-cli.md](claude-cli.md) for authorized Claude work. Do not load `docs/` to make routine selections or pass this guide to workers.
