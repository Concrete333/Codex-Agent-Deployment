# Pre-inference key audit, 11 September 2026

A separate Luna Max agent, with no parent history and read-only scope, checked
all twelve sources and drafts rather than assuming the proposed labels correct.
It independently supported errors 102/104/105/108/109/111 and clean controls
101/103/106/107/110/112. All twelve decisive quotations were exact source text.
The six worker flags were balanced across error/clean records and did not state
the required corrections. This audit was preparation, not a scored trial.

It raised two fixture caveats before freeze:

- NOTE-103's draft said "Every installation" rather than "Every upgrading
  installation". The author narrowed that phrase in the key and both participant
  copies to remove an avoidable clean-control scope ambiguity.
- NOTE-104's draft combined taking a snapshot with the unsupported key-check
  bypass. The author removed the snapshot instruction in all copies so the
  action under review is the unsupported bypass itself.

The author checked these narrow changes against the unchanged source. No labels,
impacts, quotas, sources or required findings changed. No participant had run.
Independent audit is another model's check, not independent human adjudication;
the author still knows the key. The deliberately clear errors establish a basic
diagnostic, not a representative distribution of production defects.
