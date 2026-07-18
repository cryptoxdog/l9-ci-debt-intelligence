from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml

from l9_debt_intelligence import __version__
from l9_debt_intelligence.analytics.verify import verify_analytics
from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
    sha256_bytes,
)

from .candidates import extract_candidates
from .emitters import (
    ast_grep_rule,
    generated_invariant,
    regression_fixtures,
    sdk_architecture_contract,
)
from .regression import evaluate_fixture

COMPILER_VERSION = f"l9-intelligence/{__version__}"


def write_json(path: Path, value: Any) -> str:
    encoded = canonical_json(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return sha256_bytes(canonical_json(value))


def write_yaml(path: Path, value: Any) -> str:
    text = yaml.safe_dump(
        value,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=True,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode("utf-8"))


def build_compilation(
    *,
    analysis_path: Path,
    compilation_root: Path,
) -> dict[str, Any]:
    verification = verify_analytics(analysis_path)
    candidates = extract_candidates(analysis_path)
    identity = {
        "compiler_version": COMPILER_VERSION,
        "source_snapshot_id": verification["source_snapshot_id"],
        "analysis_run_id": verification["analysis_run_id"],
        "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
    }
    compilation_id = namespaced_document_hash(
        "compile_",
        identity,
    )
    destination = compilation_root.resolve() / compilation_id
    compilation_root.resolve().mkdir(
        parents=True,
        exist_ok=True,
    )
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{compilation_id}.",
            dir=compilation_root.resolve(),
        )
    )
    try:
        artifact_hashes: dict[str, str] = {}
        artifact_hashes["candidates"] = write_json(
            temporary / "candidates.json",
            {
                "schema": "l9.candidate-rule-catalog/v1",
                "candidates": candidates,
            },
        )
        invariants = [
            generated_invariant(candidate)
            for candidate in candidates
            if candidate["state"] != "deferred"
        ]
        artifact_hashes["invariants"] = write_json(
            temporary / "generated-invariants.json",
            {
                "schema": "l9.generated-invariant-catalog/v1",
                "invariants": invariants,
            },
        )
        fixtures: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        for candidate in candidates:
            if candidate["state"] == "deferred":
                continue
            if candidate["candidate_kind"] == "ast_grep":
                artifact_hashes[f"ast-grep/{candidate['candidate_id']}"] = write_yaml(
                    temporary / "ast-grep" / f"{candidate['candidate_id']}.yaml",
                    ast_grep_rule(candidate),
                )
            if candidate["candidate_kind"] == "sdk_architecture_contract":
                artifact_hashes[f"sdk-contracts/{candidate['candidate_id']}"] = (
                    write_json(
                        temporary
                        / "sdk-contracts"
                        / f"{candidate['candidate_id']}.json",
                        sdk_architecture_contract(candidate),
                    )
                )
            candidate_fixtures = regression_fixtures(candidate)
            fixtures.extend(candidate_fixtures)
            results.extend(
                evaluate_fixture(candidate, fixture) for fixture in candidate_fixtures
            )
        artifact_hashes["regression-fixtures"] = write_json(
            temporary / "regression-fixtures.json",
            {
                "schema": "l9.regression-fixture-catalog/v1",
                "fixtures": sorted(
                    fixtures,
                    key=lambda item: item["fixture_id"],
                ),
            },
        )
        artifact_hashes["regression-results"] = write_json(
            temporary / "regression-results.json",
            {
                "schema": "l9.regression-result-catalog/v1",
                "results": sorted(
                    results,
                    key=lambda item: item["fixture_id"],
                ),
            },
        )
        passed = sum(result["status"] == "passed" for result in results)
        failed = len(results) - passed
        deterministic_document = {
            "compilation_id": compilation_id,
            "compiler_version": COMPILER_VERSION,
            "source_snapshot_id": verification["source_snapshot_id"],
            "analysis_run_id": verification["analysis_run_id"],
            "candidate_count": len(candidates),
            "compiled_candidate_count": sum(
                candidate["state"] != "deferred" for candidate in candidates
            ),
            "promotion_eligible_count": sum(
                candidate["state"] == "promotion_eligible" for candidate in candidates
            ),
            "artifact_hashes": dict(sorted(artifact_hashes.items())),
            "regression_summary": {
                "fixture_count": len(results),
                "passed": passed,
                "failed": failed,
            },
            "limitations": sorted(
                {
                    limitation
                    for candidate in candidates
                    for limitation in candidate["limitations"]
                }
            ),
        }
        manifest = {
            "schema_version": "l9.compiler-manifest/v1",
            **deterministic_document,
            "deterministic_output_hash": sha256_bytes(
                canonical_json(deterministic_document)
            ),
        }
        write_json(temporary / "manifest.json", manifest)
        if failed:
            raise RuntimeError(f"{failed} compiler regression fixtures failed")
        if destination.exists():
            existing = json.loads(
                (destination / "manifest.json").read_text(encoding="utf-8")
            )
            if (
                existing["deterministic_output_hash"]
                != manifest["deterministic_output_hash"]
            ):
                raise RuntimeError("compilation identity collision")
            shutil.rmtree(temporary)
        else:
            os.replace(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {
        "schema_version": "l9.compilation-build-result/v1",
        "compilation_id": compilation_id,
        "compilation_path": destination.as_posix(),
        "manifest_path": (destination / "manifest.json").as_posix(),
        "candidate_count": len(candidates),
        "compiled_candidate_count": sum(
            candidate["state"] != "deferred" for candidate in candidates
        ),
        "promotion_eligible_count": sum(
            candidate["state"] == "promotion_eligible" for candidate in candidates
        ),
        "deterministic_output_hash": manifest["deterministic_output_hash"],
    }
