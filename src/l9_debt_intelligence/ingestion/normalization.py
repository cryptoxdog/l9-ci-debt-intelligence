from __future__ import annotations

import unicodedata
from typing import Any

from l9_debt_intelligence.contracts.canonical import sha256_document


class NormalizationError(ValueError):
    """An event contains a value unsupported by deterministic normalization."""


def normalize_string(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def normalize_value(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        raise NormalizationError(
            "floating-point values are prohibited in corpus events"
        )
    if isinstance(value, str):
        return normalize_string(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise NormalizationError("JSON object keys must be strings")
            normalized[normalize_string(key)] = normalize_value(value[key])
        return normalized
    raise NormalizationError(f"unsupported event value type: {type(value).__name__}")


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_value(event)
    if not isinstance(normalized, dict):
        raise NormalizationError("event must normalize to an object")
    limitations = normalized.get("limitations", [])
    if isinstance(limitations, list):
        normalized["limitations"] = sorted(set(limitations))
    unknowns = normalized.get("unknowns", [])
    if isinstance(unknowns, list):
        normalized["unknowns"] = sorted(
            unknowns,
            key=lambda item: (
                str(item.get("field", "")),
                str(item.get("reason", "")),
            ),
        )
    lineage = normalized.get("lineage")
    if isinstance(lineage, dict):
        parents = lineage.get("parent_event_ids", [])
        if isinstance(parents, list):
            lineage["parent_event_ids"] = sorted(set(parents))
    return normalized


def normalized_payload_hash(event: dict[str, Any]) -> str:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        raise NormalizationError("event payload must be an object")
    return sha256_document(normalize_value(payload))
