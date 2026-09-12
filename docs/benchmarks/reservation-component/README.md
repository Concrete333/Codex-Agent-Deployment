# Held-out reservation component: search-guidance transfer

[Results — 12 September 2026](results-2026-09-12.md): both initial workers
accepted; guided worker cost 13.4% less in this single pair. No extra correction
worker or operational skill change followed.

[Frozen repeat](repeat-results-2026-09-12.md): both accepted again; guided worker
cost 13.3% less. The report separately accounts for captured supervision overhead.

[Unattended repeat](unattended-results-2026-09-12.md): both accepted, but guidance
cost 24.2% more this time. Across all three pairs, worker costs are effectively
tied. Host execution avoided live-model polling; setup and review still dominate.

This tests whether the repository-search guidance transfers to a small
implementation task. It is not a whole-skill/no-skill or solo/delegation test,
and does not compare ownership across phases. The latter remains a separate
experiment; this pair holds component ownership fixed.

## Frozen comparison

- **A:** bounded assignment without the search-guidance paragraph.
- **B:** the same assignment plus the exact paragraph tested in `context-scope`.
- Both begin with **Luna Max**, native CLI, the same tools, model controls,
  supplied Python interpreter, task, initial source and independent checks.
- Order: **B then A**, one initial session per arm, 1,200-second safety limit.
- Both own the component, callers and development tests through their attempt.
  There is no model coordinator in the measured pipeline and no paid reviewer.
- If the initial attempt returns `checks_failed`, allow at most one fresh
  **Sol High** correction, 900 seconds, using existing artifacts and the complete
  original failure output. Retain the arm's paragraph setting. Do not retry a
  substantive Luna failure on Luna, remove failing tests or supply a solution.
- A blocked runner or uncertain process ownership stops the sequence. A partial
  result is not success and does not trigger automatic repair. Maximum: four
  measured sessions, including both possible corrections.

No paid participant runs until contracts, evaluator, runtime and initial
checkouts are frozen. Attempts and repairs retain separate receipts; compute
cost through acceptance by summing all attempts for each arm. Inspect source
for structural requirements and untested contract gaps before accepting a pass.

## Task and acceptance

The previously untested synthetic service starts with a non-atomic reservation
loop and commit-only API. Workers must implement atomic duplicate aggregation,
exact tenant/SKU identity, strict validation, one-shot iterators, dry-run preview,
isolated journal records and request dispatch. The task has a small real
component/caller boundary, not the large corpus of the prior extraction test.
It is not a production portfolio implementation.

The worker sees the written contract and four public test methods. The external
grader adds twelve hidden test methods with validation subcases and a fixed-seed
100-operation sequence across tenants, commit and preview. It uses literal
expected outcomes and a separate declarative aggregate calculation; it does
not compare workers to each other. Protected source/test hashes are checked.

The host separately inspects that preview calls the shared core with
`dry_run=True`, public imports are preserved, added tests are sensible and no
out-of-scope behavior was introduced. Passing tests alone is not full acceptance.

Qualification must accept the reference and an equivalent import-alias variant;
reject the starter and six consequential mutants: preview mutation, duplicate
loss, tenant mixing, bool quantity acceptance, journal aliasing and preview
routed to commit. Each worker checkout must pass the actual Windows shell-cwd
preflight. The correct reference passes the grader in the same native sandbox.

An independent Sol High audit is preparation overhead, not a participant. It
identified a spy-based structural test that rejected a valid import alias. That
test was removed before participant execution and moved to source review. The
original unstarted preparation remains preserved; a new manifest supersedes
it explicitly. Both checkouts still receive exactly the same revised contract
and checker. The audit also added missing-key rollback and request-subclass
cases and clarified the journal's plain-list domain. An error-precedence test
was not adopted: the contract did not clearly mandate exhausting an iterator
before reporting insufficient stock. Further findings must be resolved before
freezing, not after observing model outcomes.

## Accounting and limits

Use native own-session usage, verifying model and effort for every initial and
correction attempt. Report observed errors and their repair cost, including a
failed initial attempt. Frozen historical API-equivalent rates are estimates,
not current prices, subscription consumption or actual bills.

Preparation, the fixture audit, this supervising conversation and its waiting,
offline grading and host source review are excluded from participant cost and
must not be described as free. No net whole-workflow saving is established.
One pair does not control cache variation or model randomness. A small fixture
can reveal an implementation failure but cannot establish broad model suitability.

Checkouts, evaluator qualification copies, protected manifests and receipts are
private under `AgentDeploymentBenchmarks`; the ignored `local-fixture.json`
records their location. Hidden material is withheld by assignment scope, not
an adversarial filesystem security boundary. No live project is modified.

## Commands

`python docs/benchmarks/reservation-component/experiment.py prepare` is offline.
`... experiment.py run` spends on the bounded pair and any permitted correction.
`... experiment.py summarize` reads existing usage and receipts only.
An explicit `prepare --supersede-offline` is allowed only when the previous
preparation never started; it preserves that fixture and creates a new one.

`repeat.py prepare` creates a separately identified repeat only after matching
the original source, evaluator and runtime hashes and checking request equivalence.
`repeat.py run` uses the original driver and bounds. Its pointer is the ignored
`local-repeat.json`; original results are never replaced. Use `repeat.py summarize`,
`repeat.py review --arm A|B`, and `repeat.py metrics` for saved results.
