"""Example adapter for already-normalized JSON records."""

from __future__ import annotations

from .. import common


_FIELDS = {"id", "date", "amount_minor", "currency", "memo"}


def parse(text: str) -> list[dict[str, object]]:
    value = common.strict_json_loads(text)
    if not isinstance(value, list):
        raise ValueError("canonical JSON must be a list")
    records = []
    for item in value:
        common.exact_keys(item, _FIELDS)
        records.append(
            common.record(
                id=item["id"],
                date=item["date"],
                amount_minor=item["amount_minor"],
                currency=item["currency"],
                memo=item["memo"],
            )
        )
    return common.finish(records)
