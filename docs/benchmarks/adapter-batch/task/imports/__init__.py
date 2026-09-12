"""Public transaction import API."""

from __future__ import annotations

from .adapters import (
    bank_csv,
    batch_json,
    canonical_json,
    euro_csv,
    events_jsonl,
    fixed_width,
    statement_xml,
)
from .common import require_text


_FORMATS = {
    "canonical_json": canonical_json,
    "bank_csv": bank_csv,
    "euro_csv": euro_csv,
    "events_jsonl": events_jsonl,
    "statement_xml": statement_xml,
    "fixed_width": fixed_width,
    "batch_json": batch_json,
}


def parse(format_name: str, text: str) -> list[dict[str, object]]:
    require_text(text)
    try:
        adapter = _FORMATS[format_name]
    except (KeyError, TypeError) as exc:
        raise ValueError("unknown import format") from exc
    return adapter.parse(text)


__all__ = ["parse"]
