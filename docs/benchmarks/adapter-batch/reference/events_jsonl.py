"""Reference implementation for event JSON Lines."""

from __future__ import annotations

from .. import common


_POSTED_FIELDS = {"id", "day", "minor", "currency"}


def _physical_lines(text: str):
    parts = text.split("\n")
    for index, line in enumerate(parts):
        if index < len(parts) - 1 and line.endswith("\r"):
            line = line[:-1]
        yield line


def parse(text: str) -> list[dict[str, object]]:
    common.require_text(text)
    records = []
    for line in _physical_lines(text):
        if not line.strip():
            continue
        value = common.strict_json_loads(line)
        if not isinstance(value, dict):
            raise ValueError("each JSONL line must be an object")
        status = value.get("status")
        if status != "posted" and status != "pending":
            raise ValueError("event status is missing or invalid")
        if status == "pending":
            continue
        if not _POSTED_FIELDS.issubset(value):
            raise ValueError("posted event has missing fields")
        records.append(
            common.record(
                id=value["id"],
                date=value["day"],
                amount_minor=value["minor"],
                currency=value["currency"],
                memo=value.get("memo", ""),
            )
        )
    return common.finish(records)
