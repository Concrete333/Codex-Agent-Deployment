# GPT-5.6 Luna Max repeat on the current CLI

Run one GPT-5.6 Luna Max implementation followed by one Astra High acceptance
session, using the same frozen task, prompts, policy, grader, scope and timeouts
as the [GPT-6 Luna run](luna-generation-protocol-2026-09-23.md). Preserve all
previous results. No additional paid model stages or automatic retries.

Use CLI `0.155.0-alpha.16`, matching today's GPT-6 Luna attempt; record effective
model/effort from rollouts. Requalify the independent grader before launch and
keep its results outside model context. Grade worker and final submissions
separately, record acceptance edits and reconcile own-session usage. Price
GPT-5.6 Luna at the retained rates per million: $0.20 input, $0.02 cached input,
$0.25 cache writes, $1.20 output. Astra rates remain unchanged.

The same-task Astra High solo baseline already exists: $0.755888, 27/27 methods
passing, no second reviewer. It remains historical and used an earlier CLI;
this request does not rerun it. The new old-Luna run removes the CLI-version
difference from today's Luna-to-Luna comparison, but not stochastic variation,
cache conditions, run order or possible service-side changes.

Software waits, then sends one terminal completion notification. Maximum two
paid sessions, each with a 30-minute timeout. Current task preparation/analysis
is excluded from captured pipeline cost; no subscription-saving claim.

The private `local-luna56-repeat.json` pointer locates receipts and evidence.
[Results](luna56-repeat-results-2026-09-23.md): 27/27 checks before and after
acceptance, no implementation repairs, $0.599674 captured total. Model-routing
defaults remain unchanged.
