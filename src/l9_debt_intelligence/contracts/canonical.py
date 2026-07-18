from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(document: Any) -> bytes:
    """Serialize a JSON-compatible value deterministically."""
    return json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_document(document: Any) -> str:
    return hashlib.sha256(canonical_json(document)).hexdigest()
