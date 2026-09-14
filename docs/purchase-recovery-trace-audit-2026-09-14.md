# Purchase-recovery UI delegation: targeted trace audit

Read-only audit of the 14 September Spaceships implementation. No application,
skill policy, live records or model configuration changed. No paid comparison run.

## Conclusion

Improve the assignment boundary before changing the worker model. This run shows
both real worker defects and a changing backend contract. It does not establish
that all corrections were missed initial instructions, or that another model
would have produced a cheaper accepted result.

Luna Max remains a candidate for implementing a settled UI projection. The
orchestrator should own the meaning of payment/recovery states; asking the UI
worker to infer that meaning from multiple evolving backend implementations is
not the same assignment.

## Attribution

| Distinction | Evidence available before the first UI implementation | Finding |
|---|---|---|
| Verified cancellation can resolve recovery despite `ok:false` | Worker read `purchase_recovery.unresolved`, which excludes verified cancellations, and `CashCheckoutManager._durable_public`, which emits `ok:false` for cancelled states independently of `retry_blocked`. | Existing semantics were available and inspected. The worker's classifier nonetheless required `ok:true` for cancellation. A genuine interpretation/implementation miss, not a newly added backend flag. Exact initial prompt wording is unavailable. |
| Unknown outcome is unresolved, not proof of partial progress | The plan separates inconclusive evidence from confirmed payment/reconciliation. Backend reads show unknown outcomes without success evidence. | Worker classified `outcome_unknown` and `recovery_required` as partial by state name alone, causing invalidation even without demonstrated progress. A faulty inference. The precise UI truth table was made explicit in the correction; cannot prove it was supplied initially. |
| Completed acquisition can still have an unsettled credit balance | Earlier worker reads show completed as terminal, with no `credit_balance_pending` field. Parent added that field and recovery path at 10:33:16 UTC, updating the API at 10:33:41, after the 10:21:46 dispatch. | Proven mid-assignment contract refinement. Worker incorporated it during its initial turn and added a focused assertion. Do not count this as failure to follow the initial contract. |
| Refresh polling must retain recovery outcomes | Worker created a shared portfolio result map and also a separate refresh renderer, handler and result map. The correction removed the latter and routed refresh through the shared implementation. | Worker-created duplication/integration defect. Persistence intent is visible in its own first patch. Whether the initial assignment explicitly mandated one renderer is unverified. |
| Missing credit exposure differs from explicit null | Inspected backend issue construction explicitly populated `uncertain_credit`; null represented unknown exposure. No recovered initial instruction defines omitted-field wording. | Worker initially merged missing and null into “unknown.” The correction explicitly introduced “not reported” for omission. Treat as a contract/display clarification unless the original packet is recovered, not a proven ignored instruction. |

Whitespace cleanup and locating the bundled Playwright dependency do not establish
a reasoning-capability failure. Luna completed the bounded correction round;
the parent owned the browser integration test and final acceptance.

## Smallest useful improvement

For this type of assignment, replace prose-only state guidance with a compact
input-to-behavior table or existing contract tests: payload, displayed state,
retry availability and invalidation effect. Include conflicting-looking fields
such as `ok:false` with a safely retired cancellation, and missing versus null
only where their distinction changes behavior.

Identify the shared renderer/state owner and require the actual click-to-poll
path to preserve results. Treat a new backend flag as a contract update: provide
the changed example and recheck affected behavior rather than counting it as a
worker mistake. This need not become a separate specification or approval gate.

If a worker still mishandles those settled examples, that is cleaner evidence for
reconsidering its suitability. This run alone cannot measure that counterfactual.

## Evidence and limits

- Application plan: `C:/Users/cwbec/Spaceships/plans/purchase-recovery-and-advice-implementation-2026-09-14.md`, especially its state distinctions and refresh acceptance criteria.
- Implementation report: `C:/Users/cwbec/Spaceships/plans/purchase-recovery-and-advice-implementation-report-2026-09-14.md`, delegation section.
- Parent trace: `C:/Users/cwbec/.codex/sessions/2026/09/14/rollout-2026-09-14T10-55-28-01a09f1a-933e-74e3-bd7f-84ddaed488a0_01a09f57-d596-7270-8e18-98e524f896be.jsonl`.
- Worker trace: `C:/Users/cwbec/.codex/sessions/2026/09/14/rollout-2026-09-14T11-21-46-01a09f6f-e64a-7fa0-919e-1bf24758906e.jsonl`; worker command/patch outputs also recovered through desktop task history.
- Before implementation: command `exec-e2ab18e7-0137-41ab-ad36-5a9bb2c233a1` read the initial recovery helpers; `exec-9b0b08b3-bb3e-4573-ac3c-1b983c7d80ef` read the complete durable-public result mapping. These precede the classifier patch `exec-7cb0859d-4cda-468c-ab27-cf296c64ea7c`.
- Initial balance-pending correction: `exec-47d27d22-2460-4b79-9507-6f73d1365555`. Final correction turn: `01a09f88-3289-7963-95aa-ac8ad421865d`; state correction `exec-f6dbbf0a-bd89-4722-8fbc-4b0c813eeb88`, shared-renderer cleanup `exec-6cc658e2-03aa-4a9f-ac0f-6a461480ca78`, missing-field correction `exec-77573b8a-e39d-4e7a-b17d-5c7fbd80314c`.

The original assignment and parent-to-worker messages are encrypted in the native
trace and absent from the recovered task items. The report says recovery-state
behavior was supplied, but cannot establish its exact wording. Some large source
reads are truncated in task history; conclusions above use visible code and
complete relevant patches, not assumed missing content. Historical reads, rather
than today's corrected source, establish what the worker could see at the time.
