from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json

from .errors import PublicationGateError


def reference(
    publication_manifest_path: Path,
) -> dict[str, Any]:
    manifest = json.loads(publication_manifest_path.read_text(encoding="utf-8"))
    return {
        "pack_version": manifest["pack_version"],
        "pack_id": manifest["pack_id"],
        "archive_sha256": manifest["archive_sha256"],
        "signature": manifest["signature"],
        "publication_manifest": (publication_manifest_path.resolve().as_posix()),
    }


def update_channel(
    *,
    channel: str,
    publication_manifest_path: Path,
    channel_index_path: Path,
) -> dict[str, Any]:
    current_reference = reference(publication_manifest_path)
    manifest = json.loads(publication_manifest_path.read_text(encoding="utf-8"))
    if manifest["channel"] != channel:
        raise PublicationGateError("publication manifest channel mismatch")
    previous = None
    history: list[dict[str, Any]] = []
    if channel_index_path.is_file():
        existing = json.loads(channel_index_path.read_text(encoding="utf-8"))
        previous = existing.get("active")
        history = list(existing.get("history", []))
    history.append(current_reference)
    deduplicated = {item["archive_sha256"]: item for item in history}
    index = {
        "schema_version": "l9.defense-channel-index/v1",
        "channel": channel,
        "active": current_reference,
        "previous": previous,
        "history": sorted(
            deduplicated.values(),
            key=lambda item: (
                item["pack_version"],
                item["archive_sha256"],
            ),
        ),
    }
    channel_index_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{channel_index_path.name}.",
        dir=channel_index_path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical_json(index) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, channel_index_path)
    finally:
        temporary.unlink(missing_ok=True)
    return index
