"""Reference implementation for batched JSON."""

from __future__ import annotations

from .. import common


_ROOT_FIELDS = {"currency", "batches"}
_BATCH_FIELDS = {"date", "items"}
_ITEM_FIELDS = {"id", "direction", "amount"}


def parse(text: str) -> list[dict[str, object]]:
    value = common.strict_json_loads(text)
    common.exact_keys(value, _ROOT_FIELDS)
    document_currency = common.currency(value["currency"])
    batches = value["batches"]
    if not isinstance(batches, list):
        raise ValueError("batches must be a list")

    records = []
    for batch in batches:
        common.exact_keys(batch, _BATCH_FIELDS)
        batch_date = common.iso_date(batch["date"])
        items = batch["items"]
        if not isinstance(items, list):
            raise ValueError("items must be a list")
        for item in items:
            common.exact_keys(item, _ITEM_FIELDS, {"memo"})
            direction = item["direction"]
            if direction != "in" and direction != "out":
                raise ValueError("item direction is invalid")
            amount = common.minor_units(item["amount"], allow_sign=False)
            if direction == "out":
                amount = -amount
            records.append(
                common.record(
                    id=item["id"],
                    date=batch_date,
                    amount_minor=amount,
                    currency=document_currency,
                    memo=item.get("memo", ""),
                )
            )
    return common.finish(records)
