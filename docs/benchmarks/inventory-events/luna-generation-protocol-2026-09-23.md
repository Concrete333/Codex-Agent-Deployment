# GPT-6 Luna versus the saved GPT-5.6 Luna run

Run one GPT-6 Luna Max worker on the frozen inventory component, followed by one
Astra High acceptance session. Compare with the recorded GPT-5.6 Luna Max worker
($0.0415456) and its Astra acceptance ($0.640958): $0.6825036 combined.

Reuse the exact starter, implementation prompt, result schema, independent grader
and acceptance policy snapshot from the 22 September trial. Only relocate the
acceptance prompt's evidence path. Requalify the grader on the correct controls,
starter and nine mutants before inference. Grade both the worker's original
submission and the final result; do not supply private grades to either model.

Use the original CLI configuration, sandbox and 30-minute per-stage timeouts.
The earlier executable is no longer installed, so record the current CLI version
as a comparison limitation. Verify effective model/effort from saved rollouts.
Use a fresh isolated checkout for each stage; preserve worker artifacts before
acceptance. Astra may make necessary corrections under the original protocol;
report and include those costs rather than attributing repaired work to Luna.

Maximum two paid sessions, no automatic retry or model substitution. Software
waits for each stage; one terminal notification resumes the coordinating task.

Report worker correctness, acceptance changes, input/cache/output/reasoning tokens
and full captured task cost. GPT-6 Luna standard API-equivalent rates per million
tokens are $0.10 input, $0.01 cached input, $0.125 cache writes and $0.50 output;
apply documented long-context rates when applicable. Preserve the old run's
captured rates. Sources checked 23 September: [model](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [pricing](https://developers.openai.com/api/docs/pricing).

This is one fresh observation against a historical control. Runtime changes,
cache effects and stochastic variation prevent isolating model capability from
one pair. Shared preparation and this task's supervision/analysis are excluded
from captured worker-plus-acceptance totals; no subscription-saving claim.

[Results](luna-generation-results-2026-09-23.md): both worker and final submission
passed 27/27 methods; captured worker-plus-acceptance cost was $0.524238.
The private `local-luna-generation.json` pointer locates the frozen manifest and
execution evidence. Existing model recommendations stay unchanged.
