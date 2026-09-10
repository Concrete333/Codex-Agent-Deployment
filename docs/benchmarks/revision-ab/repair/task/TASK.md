# Repair interval compaction

Fix `spans.compact_ranges(ranges)`, used to coalesce integer byte spans before
fetching them. Preserve the public signature. Add focused regression tests.

The input is a finite iterable of two-item tuples/lists `(start, end)` describing
half-open intervals. Endpoints must be integers, not bools, and start <= end.
Reject malformed pairs, invalid endpoint types or reversed ranges with
ValueError. Negative and arbitrarily large integers are valid.

Return a new list of tuples, sorted by start, merging both overlapping and
touching intervals. Drop zero-length intervals. Handle duplicates and ranges
contained inside others. Never mutate the supplied collection or its pairs.
An empty iterable returns an empty list; a generator must work too.

Only `spans.py` and new test files may be changed. Existing public tests must
remain unchanged. Use the standard library; no network, new dependencies or
external repositories. Do not inspect evaluation files or other trials. Finish
with a concise description of the change and the checks you ran.
