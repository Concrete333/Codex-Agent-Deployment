"""Reference implementation for statement XML."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from .. import common


_DOCTYPE = re.compile(r"<!\s*DOCTYPE", re.IGNORECASE)


def _whitespace_only(value: str | None) -> bool:
    return value is None or not value.strip()


def parse(text: str) -> list[dict[str, object]]:
    common.require_text(text)
    if _DOCTYPE.search(text):
        raise ValueError("DOCTYPE is forbidden")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError("malformed statement XML") from exc
    if root.tag != "statement" or set(root.attrib) != {"currency"}:
        raise ValueError("invalid statement root")
    statement_currency = common.currency(root.attrib["currency"])
    if not _whitespace_only(root.text):
        raise ValueError("text outside memo is forbidden")

    records = []
    for entry in root:
        if entry.tag != "entry" or set(entry.attrib) != {"id", "date", "amount"}:
            raise ValueError("invalid statement entry")
        if not _whitespace_only(entry.text) or not _whitespace_only(entry.tail):
            raise ValueError("text outside memo is forbidden")
        children = list(entry)
        if len(children) != 1:
            raise ValueError("entry must contain exactly one memo")
        memo = children[0]
        if memo.tag != "memo" or memo.attrib or list(memo):
            raise ValueError("invalid memo element")
        if not _whitespace_only(memo.tail):
            raise ValueError("text outside memo is forbidden")
        records.append(
            common.record(
                id=entry.attrib["id"],
                date=entry.attrib["date"],
                amount_minor=common.minor_units(entry.attrib["amount"]),
                currency=statement_currency,
                memo=memo.text or "",
            )
        )
    return common.finish(records)
