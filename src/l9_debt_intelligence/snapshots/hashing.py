from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def namespaced_document_hash(prefix: str, value: Any) -> str:
    return prefix + sha256_bytes(canonical_json(value))
