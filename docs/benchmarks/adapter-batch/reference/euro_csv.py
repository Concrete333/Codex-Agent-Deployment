"""Reference implementation for European CSV."""

from __future__ import annotations

import csv
import re
from datetime import date
from io import StringIO

from .. import common


_HEADER = {"reference", "booked", "debit", "credit", "ccy", "description"}
_EURO_DATE = re.compile(r"([0-9]{2})/([0-9]{2})/([0-9]{4})\Z")


def _date(value: str) -> str:
    match = _EURO_DATE.fullmatch(value)
    if match is None:
        raise ValueError("booked date must use DD/MM/YYYY")
    try:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1))).isoformat()
    except ValueError as exc:
        raise ValueError("booked date is not valid") from exc


def parse(text: str) -> list[dict[str, object]]:
    common.require_text(text)
    reader = csv.reader(StringIO(text, newline=""), delimiter=";", strict=True)
    header = None
    records = []
    try:
        for row in reader:
            if row == []:
                continue
            if header is None:
                if len(row) != len(_HEADER) or set(row) != _HEADER:
                    raise ValueError("invalid euro CSV header")
                header = {name: index for index, name in enumerate(row)}
                continue
            if len(row) != len(_HEADER):
                raise ValueError("euro CSV row has wrong width")
            debit = row[header["debit"]].strip()
            credit = row[header["credit"]].strip()
            if bool(debit) == bool(credit):
                raise ValueError("exactly one of debit and credit is required")
            amount = common.minor_units(
                debit or credit, allow_sign=False, decimal=","
            )
            if debit:
                amount = -amount
            records.append(
                common.record(
                    id=row[header["reference"]],
                    date=_date(row[header["booked"]]),
                    amount_minor=amount,
                    currency=row[header["ccy"]],
                    memo=row[header["description"]],
                )
            )
    except csv.Error as exc:
        raise ValueError("malformed euro CSV") from exc
    if header is None:
        raise ValueError("missing euro CSV header")
    return common.finish(records)
