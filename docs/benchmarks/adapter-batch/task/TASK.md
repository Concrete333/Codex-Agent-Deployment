# Implement six transaction-import adapters

Finish the six adapter modules used by `imports.parse(format_name, text)`.
`canonical_json` already works and shows the interface. `common.py` contains
shared normalization; reuse it. Standard library only. No network, database,
packaging changes or architecture redesign.

Every adapter returns a list of records in source order with exactly these keys:
`id`, `date`, `amount_minor`, `currency`, `memo`. Dates are ISO `YYYY-MM-DD`;
amounts are signed integer minor units (100 per unit); currency inputs are exactly
three ASCII letters in either case, with no surrounding whitespace, and normalize
to uppercase. IDs must be strings, are stripped and nonempty; memos must be strings and preserve their
text including spaces, Unicode and embedded newlines. Duplicate normalized IDs
among emitted records are errors. Use `common.record` and `common.finish` to
enforce these requirements. Helpers do not implement vendor-format parsing.

Invalid documents or records must raise `ValueError`, not return a partial
result or silently skip malformed data. Any non-string input raises `ValueError`.
Unknown fields are allowed only where stated. No external side effects.
For JSONL and fixed-width input, physical separators are LF or CRLF; a final
unterminated line is permitted. Other Unicode whitespace within a memo is data.

## Formats

### bank_csv

Comma-separated CSV with one header containing exactly `id,date,amount,currency,memo`
in any order. The header is the first nonblank CSV row. Duplicate, missing or extra header columns and wrong row widths
are errors. CSV quoting, escaped double quotes, CRLF and quoted embedded newlines
must work. Ignore completely blank rows (the CSV reader's empty row), not rows
of empty fields. Every nonblank record is emitted. Date is ISO. Amount is a
signed decimal string: optional `+`/`-`, ASCII digits, optional decimal point
followed by exactly two digits. No exponent, grouping or rounding. Use
`common.minor_units`. Surrounding amount whitespace is allowed. Header names
are exact; do not strip or case-fold them. Empty input is missing a header and
is invalid; header-only input returns `[]`. Malformed CSV quoting is invalid.

### euro_csv

Semicolon-separated CSV with header exactly `reference;booked;debit;credit;ccy;description`
in any order, with the same header/quoting/row rules as bank_csv. Date is strictly
`DD/MM/YYYY` and must represent a real date. Exactly one of debit/credit, after
stripping whitespace, must be nonempty. That amount is unsigned, uses comma
as its decimal separator and optional exactly two fractional digits; grouping,
signs and exponents are invalid. Debit becomes negative, credit positive.
Zero is valid. Map reference to id, ccy to currency, description to memo.

### events_jsonl

Each nonblank physical line is one JSON object. Blank/whitespace-only lines are
ignored. Every object needs `status`, exactly `posted` or `pending`. A pending
object is skipped without validating its other fields. A posted object needs
`id`, `day`, `minor`, `currency`; optional `memo` defaults to `""`. Extra keys are
allowed. Day is ISO; minor must be an exact integer, not bool or float. Malformed
JSON, non-object lines, missing/unknown status or invalid posted fields are
errors. Empty input returns `[]`. Duplicate IDs are checked only among posted
records. JSON duplicate object keys and non-standard NaN/Infinity are invalid,
including within ignored fields of pending objects.

### statement_xml

One XML document: `<statement currency="USD">` containing zero or more direct
`<entry id="..." date="YYYY-MM-DD" amount="-12.34"><memo>text</memo></entry>` children.
Root attributes must be exactly currency; entry attributes exactly id/date/amount.
Each entry must have exactly one memo child, with no attributes or nested elements.
Other tags/attributes, non-whitespace text outside memo, malformed XML and any
DOCTYPE declaration are invalid. Amount uses bank_csv decimal rules. XML entities
such as `&amp;` must decode normally. Empty root returns `[]`; empty text is invalid.
Comments, processing instructions and namespaces are outside the input domain.

### fixed_width

Each nonblank physical line has at least 30 characters: id in positions 0:8,
date `YYYYMMDD` in 8:16, sign `+` or `-` at 16, exactly ten ASCII minor-unit digits
in 17:27, currency in 27:30, and memo as the remaining characters. Reject invalid
width, sign, date or digit fields. The ten digits already represent minor units;
do not multiply again. Remove line endings only, preserving memo spaces.
Whitespace-only lines are ignored. Empty input returns `[]`. CRLF is supported.

### batch_json

One JSON document, an object with exactly `currency` and `batches`. Batches is a
list of objects with exactly `date` (ISO) and `items` (list). Each item has exactly
`id`, `direction`, `amount`, and optional `memo` (default `""`). Direction is
exactly `in` or `out`. Amount is an unsigned decimal string with bank_csv decimal
syntax except signs are forbidden; zero is valid. Emit every item, positive for
in and negative for out, inheriting batch date and document currency. Preserve
batch then item order. Empty batches/items are valid, but validate document
currency and each batch date even when there are no items. Reject duplicate
object keys and non-standard NaN/Infinity anywhere. Duplicate IDs across batches
are invalid.

## Work and acceptance

Modify only the six stub adapter modules. You may add `imports/adapters/_shared.py`
for shared parsing and new `test_*.py` files for regression coverage. Do not edit
the supplied API, common helpers, example, fixtures, TASK.md, conformance checker
or manifest. The API already registers all six adapters.

Run `python -B check_contract.py` and your added tests. The supplied independent
checker and fixtures are available for inspection, not modification. Passing
them does not relax any requirement above. Do not inspect external graders,
reference implementations, personal memory, other repos or other trial outputs.
Scripts and automation are allowed. Keep the final response short: changes,
actual checks/results and unresolved work.
