"""Reference implementation for bank CSV."""

from __future__ import annotations

import csv
from io import StringIO

from .. import common


_HEADER = {"id", "date", "amount", "currency", "memo"}


def parse(text: str) -> list[dict[str, object]]:
    common.require_text(text)
    reader = csv.reader(StringIO(text, newline=""), delimiter=",", strict=True)
    header = None
    records = []
    try:
        for row in reader:
            if row == []:
                continue
            if header is None:
                if len(row) != len(_HEADER) or set(row) != _HEADER:
                    raise ValueError("invalid bank CSV header")
                header = {name: index for index, name in enumerate(row)}
                continue
            if len(row) != len(_HEADER):
                raise ValueError("bank CSV row has wrong width")
            records.append(
                common.record(
                    id=row[header["id"]],
                    date=row[header["date"]],
                    amount_minor=common.minor_units(row[header["amount"]]),
                    currency=row[header["currency"]],
                    memo=row[header["memo"]],
                )
            )
    except csv.Error as exc:
        raise ValueError("malformed bank CSV") from exc
    if header is None:
        raise ValueError("missing bank CSV header")
    return common.finish(records)
