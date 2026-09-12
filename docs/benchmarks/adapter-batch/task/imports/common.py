"""Shared validation and normalization for transaction imports."""

from __future__ import annotations

import json
import re
from datetime import date as _date
from typing import Any, Iterable, Mapping


_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
_CURRENCY = re.compile(r"[A-Za-z]{3}\Z")


def require_text(text: Any) -> str:
    if not isinstance(text, str):
        raise ValueError("input must be a string")
    return text


def iso_date(value: Any) -> str:
    if not isinstance(value, str) or _ISO_DATE.fullmatch(value) is None:
        raise ValueError("date must use YYYY-MM-DD")
    try:
        _date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("date is not valid") from exc
    return value


def currency(value: Any) -> str:
    if not isinstance(value, str) or _CURRENCY.fullmatch(value) is None:
        raise ValueError("currency must be three ASCII letters")
    return value.upper()


_normalize_currency = currency


def minor_units(
    value: Any, *, allow_sign: bool = True, decimal: str = "."
) -> int:
    """Parse a decimal amount exactly, without floating-point arithmetic."""
    if not isinstance(value, str):
        raise ValueError("amount must be a string")
    value = value.strip()
    if decimal not in {".", ","}:
        raise ValueError("unsupported decimal separator")
    sign = r"[+-]?" if allow_sign else ""
    pattern = re.compile(sign + r"([0-9]+)(?:" + re.escape(decimal) + r"([0-9]{2}))?\Z")
    match = pattern.fullmatch(value)
    if match is None:
        raise ValueError("amount has invalid decimal syntax")
    magnitude = int(match.group(1)) * 100 + int(match.group(2) or "00")
    return -magnitude if value.startswith("-") else magnitude


def strict_json_loads(text: Any) -> Any:
    """Decode JSON while rejecting duplicate keys and non-standard constants."""
    require_text(text)

    def object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise ValueError(f"invalid JSON constant: {value}")

    try:
        return json.loads(
            text,
            object_pairs_hook=object_from_pairs,
            parse_constant=reject_constant,
        )
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("invalid JSON") from exc


def exact_keys(
    value: Any, required: Iterable[str], optional: Iterable[str] = ()
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("expected an object")
    required_set = set(required)
    allowed = required_set | set(optional)
    keys = set(value)
    if not required_set.issubset(keys) or not keys.issubset(allowed):
        raise ValueError("object has missing or unknown fields")
    return value


def record(
    *, id: Any, date: Any, amount_minor: Any, currency: Any, memo: Any
) -> dict[str, Any]:
    if not isinstance(id, str):
        raise ValueError("id must be a string")
    normalized_id = id.strip()
    if not normalized_id:
        raise ValueError("id must not be empty")
    if isinstance(amount_minor, bool) or not isinstance(amount_minor, int):
        raise ValueError("amount_minor must be an integer")
    if not isinstance(memo, str):
        raise ValueError("memo must be a string")
    return {
        "id": normalized_id,
        "date": iso_date(date),
        "amount_minor": amount_minor,
        "currency": _normalize_currency(currency),
        "memo": memo,
    }


def finish(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = list(records)
    seen: set[str] = set()
    for item in result:
        identifier = item["id"]
        if identifier in seen:
            raise ValueError("duplicate normalized id")
        seen.add(identifier)
    return result
