# Evaluation contract, version 2

The original TASK.md interfaces and requirements still apply. These clarifications
are supplied equally to every condition in any new version-2 trial.

- Retry delays measure elapsed seconds. Add them to the UTC instant, including
  when the supplied timezone changes its offset during the delay. HTTP dates
  also refer to instants, not local wall-clock arithmetic.
- Required numeric coverage is finite nonnegative Python `int` and `float`
  values representable as finite binary64 seconds. Policy calculations may
  round to binary64 precision; scheduling uses datetime's microsecond precision
  and representable range. Large attempt counts must saturate without huge
  intermediate integers. Required negative/nonfinite values remain invalid.
- Arbitrary-precision numeric objects, values outside that range, and scheduling
  beyond datetime's representable range are not additional acceptance gates.
  Supporting them is optional; do not sacrifice ordinary correctness for them.
- CSV money remains exact decimal cents, independent of the ambient Decimal
  precision. Trailing zeroes are valid; a nonzero fractional cent is invalid
  even when it appears far beyond the default arithmetic precision.

Tests must exercise the stated behavior, not just copy implementation assumptions.
