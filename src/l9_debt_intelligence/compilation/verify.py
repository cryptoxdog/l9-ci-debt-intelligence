from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    sha256_bytes,
    sha256_file,
)

from .errors import CompilationVerificationError


def verify_compilation(path: Path) -> dict[str, Any]:
    path = path.resolve()
    manifest_path = path / "manifest.json"
    if not manifest_path.is_file():
        raise CompilationVerificationError("compiler manifest does not exist")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "l9.compiler-manifest/v1":
        raise CompilationVerificationError("unsupported compiler manifest")
    if manifest.get("compilation_id") != path.name:
        raise CompilationVerificationError("compilation directory identity mismatch")
    file_map = {
        "candidates": path / "candidates.json",
        "invariants": path / "generated-invariants.json",
        "regression-fixtures": (path / "regression-fixtures.json"),
        "regression-results": (path / "regression-results.json"),
    }
    for key, expected_hash in manifest["artifact_hashes"].items():
        artifact = file_map.get(key)
        if artifact is None:
            prefix, candidate_id = key.split("/", 1)
            extension = "yaml" if prefix == "ast-grep" else "json"
            artifact = path / prefix / f"{candidate_id}.{extension}"
        if not artifact.is_file():
            raise CompilationVerificationError(f"missing compiler artifact: {key}")
        if artifact.suffix == ".json":
            document = json.loads(artifact.read_text(encoding="utf-8"))
            actual = sha256_bytes(canonical_json(document))
        else:
            actual = sha256_file(artifact)
        if actual != expected_hash:
            raise CompilationVerificationError(
                f"compiler artifact hash mismatch: {key}"
            )
    deterministic_document = {
        key: manifest[key]
        for key in (
            "compilation_id",
            "compiler_version",
            "source_snapshot_id",
            "analysis_run_id",
            "candidate_count",
            "compiled_candidate_count",
            "promotion_eligible_count",
            "artifact_hashes",
            "regression_summary",
            "limitations",
        )
    }
    output_hash = sha256_bytes(canonical_json(deterministic_document))
    if output_hash != manifest["deterministic_output_hash"]:
        raise CompilationVerificationError("compiler deterministic hash mismatch")
    if manifest["regression_summary"]["failed"] != 0:
        raise CompilationVerificationError("compiler regressions contain failures")
    return {
        "schema_version": "l9.compilation-verification/v1",
        "status": "valid",
        "compilation_id": manifest["compilation_id"],
        "source_snapshot_id": manifest["source_snapshot_id"],
        "analysis_run_id": manifest["analysis_run_id"],
        "candidate_count": manifest["candidate_count"],
        "verified_artifact_count": len(manifest["artifact_hashes"]),
        "deterministic_output_hash": output_hash,
    }
