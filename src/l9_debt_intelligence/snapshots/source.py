from __future__ import annotations

import json
from pathlib import Path

from l9_debt_intelligence.contracts.canonical import sha256_document
from l9_debt_intelligence.ingestion.verify import verify_store

from .errors import SnapshotSourceError
from .models import SnapshotRecord


def load_verified_records(storage_root: Path) -> tuple[SnapshotRecord, ...]:
    verification = verify_store(storage_root)
    if verification.get("status") != "valid":
        raise SnapshotSourceError("ingestion store verification did not return valid")
    records_root = storage_root / "records"
    records: list[SnapshotRecord] = []
    for path in sorted(records_root.glob("cr_*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise SnapshotSourceError(f"record is not an object: {path}")
        payload_reference = document.get("payload_reference")
        if not isinstance(payload_reference, dict):
            raise SnapshotSourceError(f"record has no payload_reference: {path}")
        record_id = document.get("record_id")
        if record_id != path.stem:
            raise SnapshotSourceError(
                f"record identity does not match filename: {path}"
            )
        lifecycle_state = document.get("lifecycle_state")
        if lifecycle_state in {"RETRACTED", "REJECTED", "QUARANTINED"}:
            continue
        limitations = document.get("limitations", [])
        if not isinstance(limitations, list):
            raise SnapshotSourceError(f"record limitations must be a list: {path}")
        records.append(
            SnapshotRecord(
                record_id=str(record_id),
                source_event_id=str(document["source_event_id"]),
                producer_id=str(document["producer_id"]),
                event_class=str(document["event_class"]),
                lifecycle_state=str(lifecycle_state),
                redaction_status=str(document["redaction_status"]),
                producer_contract=str(payload_reference["producer_contract"]),
                payload_content_hash=str(payload_reference["content_hash"]),
                limitations_json=json.dumps(
                    sorted(set(str(item) for item in limitations)),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                superseded_by=(
                    str(document["superseded_by"])
                    if document.get("superseded_by")
                    else None
                ),
                source_record_hash=sha256_document(document),
            )
        )
    return tuple(sorted(records, key=lambda value: value.record_id))
