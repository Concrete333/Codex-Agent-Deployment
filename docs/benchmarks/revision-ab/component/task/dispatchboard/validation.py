"""Validation shared by direct and idempotent ingestion paths."""

import copy
import json
import math


def validate_tenant(value):
    if type(value) is not str or not 1 <= len(value) <= 128 or value != value.strip():
        raise ValueError("tenant must be a 1-128 character unpadded string")
    return value


def _validate_json(value, active=None):
    if active is None:
        active = set()
    kind = type(value)
    if value is None or kind in (bool, int, str):
        return
    if kind is float:
        if not math.isfinite(value):
            raise ValueError("JSON numbers must be finite")
        return
    if kind is list:
        identity = id(value)
        if identity in active:
            raise ValueError("payload must be an acyclic JSON tree")
        active.add(identity)
        try:
            for item in value:
                _validate_json(item, active)
        finally:
            active.remove(identity)
        return
    if kind is dict:
        identity = id(value)
        if identity in active:
            raise ValueError("payload must be an acyclic JSON tree")
        active.add(identity)
        try:
            for key, item in value.items():
                if type(key) is not str:
                    raise ValueError("JSON object keys must be strings")
                _validate_json(item, active)
        finally:
            active.remove(identity)
        return
    raise ValueError("payload contains a value outside the supported JSON types")


def snapshot_json(payload):
    _validate_json(payload)
    return copy.deepcopy(payload)


def canonical_json(payload):
    _validate_json(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
