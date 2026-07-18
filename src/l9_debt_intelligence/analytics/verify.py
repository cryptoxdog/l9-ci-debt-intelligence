from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import sha256_bytes

from .builder import REPORT_FILES
from .errors import AnalyticsVerificationError


def verify_analytics(path: Path) -> dict[str, Any]:
    path = path.resolve()
    manifest_path = path / "manifest.json"
    if not manifest_path.is_file():
        raise AnalyticsVerificationError("analysis manifest does not exist")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "l9.analysis-manifest/v1":
        raise AnalyticsVerificationError("unsupported analysis manifest schema")
    if manifest.get("analysis_run_id") != path.name:
        raise AnalyticsVerificationError("analysis directory identity mismatch")
    report_hashes = manifest.get("report_hashes")
    if not isinstance(report_hashes, dict):
        raise AnalyticsVerificationError("report_hashes must be an object")
    for name, filename in REPORT_FILES.items():
        report_path = path / filename
        if not report_path.is_file():
            raise AnalyticsVerificationError(f"missing report: {filename}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        actual_hash = sha256_bytes(canonical_json(report))
        if actual_hash != report_hashes.get(name):
            raise AnalyticsVerificationError(f"report hash mismatch: {filename}")
        if report.get("source_snapshot_id") != manifest.get("source_snapshot_id"):
            raise AnalyticsVerificationError(f"report snapshot mismatch: {filename}")
    deterministic_document = {
        "analysis_run_id": manifest["analysis_run_id"],
        "source_snapshot_id": manifest["source_snapshot_id"],
        "observation_count": manifest["observation_count"],
        "report_hashes": manifest["report_hashes"],
        "limitations": manifest["limitations"],
    }
    output_hash = sha256_bytes(canonical_json(deterministic_document))
    if output_hash != manifest.get("deterministic_output_hash"):
        raise AnalyticsVerificationError("analysis deterministic output hash mismatch")
    return {
        "schema_version": "l9.analysis-verification/v1",
        "status": "valid",
        "analysis_run_id": manifest["analysis_run_id"],
        "source_snapshot_id": manifest["source_snapshot_id"],
        "observation_count": manifest["observation_count"],
        "verified_report_count": len(REPORT_FILES),
        "deterministic_output_hash": output_hash,
    }
