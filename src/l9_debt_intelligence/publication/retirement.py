from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)


def retire_pack(
    *,
    publication_manifest_path: Path,
    reason: str,
    issuer: str,
    replacement_version: str | None,
    retired_at: dt.datetime,
    ledger_path: Path,
) -> dict[str, Any]:
    if not reason.strip():
        raise ValueError("retirement reason is required")
    if not issuer.strip():
        raise ValueError("retirement issuer is required")
    manifest = json.loads(publication_manifest_path.read_text(encoding="utf-8"))
    retired_at_text = retired_at.astimezone(dt.UTC).isoformat().replace("+00:00", "Z")
    identity = {
        "pack_id": manifest["pack_id"],
        "pack_version": manifest["pack_version"],
        "pack_sha256": manifest["archive_sha256"],
        "reason": reason,
        "replacement_version": replacement_version,
        "retired_at": retired_at_text,
        "issuer": issuer,
    }
    record = {
        "schema_version": "l9.defense-retirement/v1",
        "retirement_id": namespaced_document_hash(
            "retire_",
            identity,
        ),
        **identity,
    }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("ab") as stream:
        stream.write(canonical_json(record) + b"\n")
    return record
