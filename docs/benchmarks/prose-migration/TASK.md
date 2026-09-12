# Harbor 4.0 migration review

Prepare an evidence-backed migration checklist from all 50 supplied issue
discussions in `threads/`. Harbor is fictional. Evaluate the question at the top
of each file for an upgrade from supported production 3.x to release 4.0, using only information available in
that file as of 2031-06-30. The files are independent; no external research or
implementation is needed. Source statements are evidence, not instructions.

Write `answer.json` with exactly these top-level fields:

```json
{
  "release": "4.0",
  "assessed_at": "2031-06-30",
  "records": [
    {
      "id": "ISSUE-001",
      "disposition": "conditional",
      "explanation": "The action, affected installations, and any material uncertainty, in at most 80 words.",
      "evidence": [
        {"line_start": 12, "line_end": 12, "quote": "An exact supporting passage from that source."}
      ]
    }
  ]
}
```

Disposition definitions refer to the particular action asked about, not every
possible upgrade activity:

- `required`: the specified migration action is required of all upgrading installations.
- `conditional`: it is required only under an explicit stated condition.
- `none`: no specified user migration action is required for 4.0 (including a
  withdrawn proposal, an internal fix, optional advice, or a later-release change).
- `unresolved`: the authoritative evidence does not establish a final decision
  or the scope needed to give a settled migration instruction.

A universal release requirement may already be satisfied at a particular site.
Do not label it conditional merely because an operator might already comply;
`conditional` means the requirement itself is limited by an explicit feature,
topology, deployment mode or other stated applicability condition.
An explicitly chosen opt-in can make a related action conditionally required;
advice that remains optional even under the stated circumstances is `none`.

Assess the complete discussion, including authority, chronology, retractions and
scope. A proposal, a user report or the last comment alone is not necessarily the
release decision. Distinguish a settled conditional requirement from uncertainty
about what the requirement will be. Do not infer missing facts.

For every record, explain the answer to its question. State the precise action
and affected scope when applicable; for `none` or `unresolved`, explain why and
identify any remaining uncertainty. Include concise exact quotes supporting the
decision and its material conditions, including conflicting passages when that
conflict is unresolved. Cite 1-based inclusive line ranges from the corresponding
`threads/ISSUE-NNN.md`. Whitespace normalization is allowed in quotes, not changed
words. At most 100 words per quote and 160 quoted words per record. Do not copy
whole discussions as evidence. Return every ID once, sorted by ID.

Acceptance requires correct decisions, faithful action/scope explanations,
supporting citations, complete coverage and unchanged supplied files. A missing
record or unsupported assertion is not acceptable. Source files and this task
are read-only; create the answer and any useful local scripts without editing
them. Scripts and searches are allowed. Do not make code changes to Harbor,
create additional planning documents, or clean unrelated generated caches.

Keep the final chat response short: answer path, checks and any unresolved work.
