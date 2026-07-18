from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import sha256_bytes

from .errors import EffectivenessVerificationError


def verify_effectiveness_report(
    report_directory: Path,
) -> dict[str, Any]:
    report_directory = report_directory.resolve()
    report_path = report_directory / "effectiveness-report.json"
    manifest_path = report_directory / "manifest.json"
    if not report_path.is_file() or not manifest_path.is_file():
        raise EffectivenessVerificationError(
            "effectiveness report or manifest is missing"
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if report["report_id"] != report_directory.name:
        raise EffectivenessVerificationError("report directory identity mismatch")
    if manifest["report_id"] != report["report_id"]:
        raise EffectivenessVerificationError("manifest report identity mismatch")
    actual_hash = sha256_bytes(canonical_json(report))
    if actual_hash != manifest["report_sha256"]:
        raise EffectivenessVerificationError("effectiveness report hash mismatch")
    if manifest["outcome_snapshot_hash"] != report["outcome_snapshot_hash"]:
        raise EffectivenessVerificationError("outcome snapshot lineage mismatch")
    return {
        "schema_version": "l9.effectiveness-verification/v1",
        "status": "valid",
        "report_id": report["report_id"],
        "pack_id": report["pack_id"],
        "pack_version": report["pack_version"],
        "observation_count": report["observation_count"],
        "report_sha256": actual_hash,
    }
