"""Reference implementation for fixed-width records."""

from __future__ import annotations

import re
from datetime import date

from .. import common


_COMPACT_DATE = re.compile(r"([0-9]{4})([0-9]{2})([0-9]{2})\Z")
_MINOR = re.compile(r"[0-9]{10}\Z")


def _physical_lines(text: str):
    parts = text.split("\n")
    for index, line in enumerate(parts):
        if index < len(parts) - 1 and line.endswith("\r"):
            line = line[:-1]
        yield line


def _date(value: str) -> str:
    match = _COMPACT_DATE.fullmatch(value)
    if match is None:
        raise ValueError("fixed-width date must use YYYYMMDD")
    try:
        return date(*(int(part) for part in match.groups())).isoformat()
    except ValueError as exc:
        raise ValueError("fixed-width date is not valid") from exc


def parse(text: str) -> list[dict[str, object]]:
    common.require_text(text)
    records = []
    for line in _physical_lines(text):
        if not line.strip():
            continue
        if len(line) < 30:
            raise ValueError("fixed-width row is too short")
        sign = line[16]
        digits = line[17:27]
        if sign not in {"+", "-"} or _MINOR.fullmatch(digits) is None:
            raise ValueError("invalid fixed-width amount")
        amount = int(digits)
        if sign == "-":
            amount = -amount
        records.append(
            common.record(
                id=line[0:8],
                date=_date(line[8:16]),
                amount_minor=amount,
                currency=line[27:30],
                memo=line[30:],
            )
        )
    return common.finish(records)
