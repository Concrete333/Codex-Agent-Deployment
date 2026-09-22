# Sol solo versus delegated implementation

[Fresh three-arm repeat](repeat-results-2026-09-22.md): all final submissions
passed the revised 254-case fixture. Sol + Luna cost 19.8% less than fresh solo,
including one review repair. MiMo produced no artifact; Sol implemented locally.
A post-hoc XML probe exposes a reference/coverage gap, recorded separately.

[First paired result](results-2026-09-21.md): both final submissions passed;
delegation used less Codex usage but cost 7.4% more on the combined estimate.
Includes harness recovery and worker-failure caveats.

[Luna follow-up](luna-results-2026-09-22.md): Sol High + Luna Max passed the same
244 cases without coordinator repairs, at 30.1% lower estimated execution cost
than the retained Sol-solo baseline. One run, not a general savings claim.

[Uncapped MiMo follow-up](uncapped-results-2026-09-22.md): complete handoff in
22 steps, 244/244 cases, $0.684 combined estimate. A post-hoc reference mismatch
remains, so this is not evidence of equal accuracy at lower cost.

## Original paired screening protocol

One paired screening run on the six-adapter fixture, reconstructed from the
committed version-two inputs: 146 visible and 98 held-out cases. This tests a
known, bounded implementation task, not open-ended debugging or unseen routing.

- **Solo:** Sol High implements, checks and corrects its own result.
- **Delegated:** Sol High reads the Kilo skill and prepares one assignment.
  Software runs MiMo-V2.6-Pro with thinking through the installed Kilo wrapper,
  then resumes the same Sol session for acceptance and any local corrections.

Both arms receive identical starting code, requirements and write scope. Neither
sees the reference, held-out cases or previous solutions. The independent grader
runs after model work; its results are not fed back for repair. The reference
must pass and broken controls must fail before any paid call.

Count Sol preparation, implementation, review and repair usage, plus the Kilo
attempt whether successful or not. Report Codex tokens separately from Kilo's
reported cost, and distinguish API-equivalent estimates from subscription usage.
Experiment construction and supervision are separate research overhead, not
included in task execution cost. No extra reviewer is added to the solo arm.

There is one Kilo attempt, with the configured 30-step limit and a 30-minute
timeout. Each Sol stage has a 30-minute timeout. No paid stage retries
automatically. Software waits; a terminal callback wakes the supervising task.

Limitations: one run per arm, solo first, different CLI/tool scaffolds, and a
previously used fixture. This measures this deployment path, not an isolated
model ranking or proof of general savings. Failures and runtime repairs remain
in the record; a rejected or partial artifact is not a completed implementation.

`experiment.py prepare` qualifies and freezes the inputs without inference.
`experiment.py run` spends on the two arms. The ignored `local-fixture.json`
points to retained local evidence. Existing runs are never overwritten.
