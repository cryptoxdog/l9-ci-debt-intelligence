from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .storage import FilesystemCorpusStore


class LedgerVerificationError(RuntimeError):
    """The ingestion ledger or immutable objects are inconsistent."""


def verify_store(root: Path) -> dict[str, Any]:
    store = FilesystemCorpusStore(root)
    store.initialize()
    entries: list[dict[str, Any]] = []
    with store.ledger_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise LedgerVerificationError(
                    f"ledger line {line_number} is not an object"
                )
            expected_sequence = len(entries) + 1
            if value.get("sequence") != expected_sequence:
                raise LedgerVerificationError(
                    f"ledger sequence gap at line {line_number}"
                )
            entries.append(value)
    accepted = 0
    duplicates = 0
    quarantined = 0
    for entry in entries:
        disposition = entry["disposition"]
        if disposition == "accepted":
            accepted += 1
        elif disposition == "duplicate":
            duplicates += 1
        elif disposition == "quarantined":
            quarantined += 1
        record_id = entry.get("record_id")
        if record_id:
            record = store.read_record(record_id)
            if record is None:
                raise LedgerVerificationError(
                    f"ledger references missing record {record_id}"
                )
    return {
        "schema": "l9.ingestion-verification/v1",
        "status": "valid",
        "ledger_entries": len(entries),
        "accepted": accepted,
        "duplicates": duplicates,
        "quarantined": quarantined,
        "record_count": len(list(store.records_path.glob("cr_*.json"))),
        "quarantine_count": len(list(store.quarantine_path.glob("qr_*.json"))),
    }
