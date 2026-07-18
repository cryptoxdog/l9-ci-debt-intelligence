from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
    sha256_bytes,
)

from .metrics import (
    cooccurrence_rows,
    effectiveness_rows,
    effort_rows,
    recurrence_rows,
)
from .projection import load_observations

REPORT_FILES = {
    "recurrence": "recurrence-report.json",
    "cooccurrence": "cooccurrence-matrix.json",
    "effort": "effort-atlas.json",
    "effectiveness": "rule-effectiveness.json",
}


def report_document(
    schema_version: str,
    snapshot_id: str,
    rows: list[dict[str, object]],
    limitations: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "source_snapshot_id": snapshot_id,
        "rows": rows,
        "limitations": sorted(set(limitations)),
    }


def build_analytics(
    *,
    snapshot_path: Path,
    analytics_root: Path,
) -> dict[str, Any]:
    snapshot_path = snapshot_path.resolve()
    snapshot_id = snapshot_path.name
    observations = load_observations(snapshot_path)
    limitations: list[str] = []
    if any(item.occurrence_scope.startswith("record:") for item in observations):
        limitations.append(
            "occurrence_scope unavailable for some records; "
            "record identity was used as a non-cooccurring fallback"
        )
    if any(item.canonical_rule_id is None for item in observations):
        limitations.append("canonical_rule_id unavailable for some records")
    if any(item.effort_minutes is None for item in observations):
        limitations.append("effort_minutes unavailable for some records")
    reports = {
        "recurrence": report_document(
            "l9.recurrence-report/v1",
            snapshot_id,
            recurrence_rows(observations),
            limitations,
        ),
        "cooccurrence": report_document(
            "l9.cooccurrence-matrix/v1",
            snapshot_id,
            cooccurrence_rows(observations),
            limitations,
        ),
        "effort": report_document(
            "l9.effort-atlas/v1",
            snapshot_id,
            effort_rows(observations),
            limitations,
        ),
        "effectiveness": report_document(
            "l9.rule-effectiveness/v1",
            snapshot_id,
            effectiveness_rows(observations),
            limitations,
        ),
    }
    report_hashes = {
        name: sha256_bytes(canonical_json(document))
        for name, document in sorted(reports.items())
    }
    identity_document = {
        "source_snapshot_id": snapshot_id,
        "analytics_contract_version": ("l9.intelligence-analytics-contract/v1"),
        "report_hashes": report_hashes,
    }
    analysis_run_id = namespaced_document_hash(
        "ar_",
        identity_document,
    )
    deterministic_document = {
        "analysis_run_id": analysis_run_id,
        "source_snapshot_id": snapshot_id,
        "observation_count": len(observations),
        "report_hashes": report_hashes,
        "limitations": sorted(set(limitations)),
    }
    manifest = {
        "schema_version": "l9.analysis-manifest/v1",
        **deterministic_document,
        "deterministic_output_hash": sha256_bytes(
            canonical_json(deterministic_document)
        ),
    }
    destination = analytics_root.resolve() / analysis_run_id
    analytics_root.resolve().mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{analysis_run_id}.",
            dir=analytics_root.resolve(),
        )
    )
    try:
        for name, document in reports.items():
            (temporary / REPORT_FILES[name]).write_bytes(
                canonical_json(document) + b"\n"
            )
        (temporary / "manifest.json").write_bytes(canonical_json(manifest) + b"\n")
        if destination.exists():
            existing = json.loads(
                (destination / "manifest.json").read_text(encoding="utf-8")
            )
            if (
                existing.get("deterministic_output_hash")
                != manifest["deterministic_output_hash"]
            ):
                raise RuntimeError("analysis identity collision with different output")
            shutil.rmtree(temporary)
        else:
            os.replace(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {
        "schema_version": "l9.analysis-build-result/v1",
        "analysis_run_id": analysis_run_id,
        "source_snapshot_id": snapshot_id,
        "analysis_path": destination.as_posix(),
        "manifest_path": (destination / "manifest.json").as_posix(),
        "observation_count": len(observations),
        "deterministic_output_hash": (manifest["deterministic_output_hash"]),
    }
