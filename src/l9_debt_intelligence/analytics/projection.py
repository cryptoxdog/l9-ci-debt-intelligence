from __future__ import annotations

import hashlib
from pathlib import Path

import pyarrow.parquet as pq

from l9_debt_intelligence.snapshots.verify import verify_snapshot

from .models import LearningObservation


def fallback_scope(record_id: str) -> str:
    return f"record:{record_id}"


def load_observations(
    snapshot_path: Path,
) -> tuple[LearningObservation, ...]:
    verify_snapshot(snapshot_path)
    snapshot_path = snapshot_path.resolve()
    observations: list[LearningObservation] = []
    manifest_path = snapshot_path / "manifest.json"
    import json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for partition in manifest["partitions"]:
        table = pq.ParquetFile(snapshot_path / partition["relative_path"]).read()
        columns = set(table.column_names)
        for row in table.to_pylist():
            record_id = str(row["record_id"])
            payload_hash = str(row["payload_content_hash"])
            occurrence_scope = row.get("occurrence_scope")
            if not isinstance(occurrence_scope, str) or not occurrence_scope:
                occurrence_scope = fallback_scope(record_id)
            fingerprint = row.get("recurrence_fingerprint")
            if not isinstance(fingerprint, str) or len(fingerprint) != 64:
                fingerprint = hashlib.sha256(
                    (str(row["event_class"]) + "\0" + payload_hash).encode("utf-8")
                ).hexdigest()
            effort = row.get("effort_minutes")
            if not isinstance(effort, int) or effort < 0:
                effort = None
            observations.append(
                LearningObservation(
                    record_id=record_id,
                    producer_id=str(row["producer_id"]),
                    event_class=str(row["event_class"]),
                    producer_contract=str(row["producer_contract"]),
                    occurrence_scope=occurrence_scope,
                    recurrence_fingerprint=fingerprint,
                    canonical_rule_id=(
                        row.get("canonical_rule_id")
                        if "canonical_rule_id" in columns
                        else None
                    ),
                    repository_identity=(
                        row.get("repository_identity")
                        if "repository_identity" in columns
                        else None
                    ),
                    component=(
                        row.get("component") if "component" in columns else None
                    ),
                    remediation_class=(
                        row.get("remediation_class")
                        if "remediation_class" in columns
                        else None
                    ),
                    effort_minutes=effort,
                    validation_outcome=(
                        row.get("validation_outcome")
                        if "validation_outcome" in columns
                        else None
                    ),
                    false_positive_disposition=(
                        row.get("false_positive_disposition")
                        if "false_positive_disposition" in columns
                        else None
                    ),
                    pack_version=(
                        row.get("pack_version") if "pack_version" in columns else None
                    ),
                )
            )
    return tuple(
        sorted(
            observations,
            key=lambda item: item.record_id,
        )
    )
