from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from l9_debt_intelligence.compilation.verify import (
    verify_compilation,
)
from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
    sha256_bytes,
    sha256_file,
)

from .archive import build_deterministic_archive
from .compatibility import load_compatibility, parse_version
from .errors import PublicationGateError


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PublicationGateError(f"expected JSON object: {path}")
    return value


def canonical_rule_id(candidate_id: str) -> str:
    return "l9.debt." + candidate_id.removeprefix("candidate_")[:32]


def source_for_candidate(
    *,
    compilation_path: Path,
    candidate: dict[str, Any],
) -> tuple[str, Path]:
    candidate_id = candidate["candidate_id"]
    kind = candidate["candidate_kind"]
    if kind == "ast_grep":
        relative = Path(f"ast-grep/{candidate_id}.yaml")
    elif kind == "sdk_architecture_contract":
        relative = Path(f"sdk-contracts/{candidate_id}.json")
    else:
        relative = Path("generated-invariants.json")
    source = compilation_path / relative
    if not source.is_file():
        raise PublicationGateError(
            f"compiled candidate artifact is missing: {relative}"
        )
    return kind, source


def assemble_pack(
    *,
    compilation_path: Path,
    output_root: Path,
    version: str,
    taxonomy_version: str,
    sdk_contract_version: str,
    compatibility_path: Path,
) -> dict[str, Any]:
    parse_version(version)
    verification = verify_compilation(compilation_path)
    compiler_manifest = load_json(compilation_path / "manifest.json")
    if compiler_manifest["regression_summary"]["failed"] != 0:
        raise PublicationGateError("compiler regressions contain failures")
    compatibility = load_compatibility(compatibility_path)
    if compatibility["sdk"]["contract"] != sdk_contract_version:
        raise PublicationGateError("SDK contract does not match compatibility matrix")
    catalog = load_json(compilation_path / "candidates.json")
    candidates = catalog.get("candidates", [])
    eligible = sorted(
        (
            candidate
            for candidate in candidates
            if candidate.get("state") == "promotion_eligible"
        ),
        key=lambda item: item["candidate_id"],
    )
    if not eligible:
        raise PublicationGateError("no promotion-eligible candidates are available")
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(
            prefix=".defense-pack.",
            dir=output_root,
        )
    )
    try:
        rules_root = temporary / "rules"
        rules_root.mkdir(parents=True)
        rules: list[dict[str, Any]] = []
        checksums: dict[str, str] = {}
        for candidate in eligible:
            kind, source = source_for_candidate(
                compilation_path=compilation_path,
                candidate=candidate,
            )
            extension = source.suffix
            relative = Path("rules") / f"{candidate['candidate_id']}{extension}"
            destination = temporary / relative
            destination.write_bytes(source.read_bytes())
            checksum = sha256_file(destination)
            checksums[relative.as_posix()] = checksum
            rules.append(
                {
                    "canonical_rule_id": canonical_rule_id(candidate["candidate_id"]),
                    "candidate_id": candidate["candidate_id"],
                    "kind": kind,
                    "score": candidate["score"],
                    "source_path": relative.as_posix(),
                    "source_sha256": checksum,
                    "lineage": {
                        "corpus_snapshot": verification["source_snapshot_id"],
                        "analysis_run": verification["analysis_run_id"],
                        "compilation_id": verification["compilation_id"],
                        "recurrence_fingerprint": candidate["recurrence_fingerprint"],
                    },
                }
            )
        compatibility_bytes = canonical_json(compatibility) + b"\n"
        (temporary / "compatibility.json").write_bytes(compatibility_bytes)
        checksums["compatibility.json"] = sha256_bytes(compatibility_bytes)
        identity = {
            "protocol": "l9.debt-defense/v1",
            "version": version,
            "corpus_snapshot": verification["source_snapshot_id"],
            "analysis_run": verification["analysis_run_id"],
            "compilation_id": verification["compilation_id"],
            "compiler_version": compiler_manifest["compiler_version"],
            "taxonomy_version": taxonomy_version,
            "SDK_contract_version": sdk_contract_version,
            "compatibility": compatibility,
            "rules": rules,
            "checksums": dict(sorted(checksums.items())),
        }
        pack_id = namespaced_document_hash(
            "pack_",
            identity,
        )
        pack = {
            "schema_version": "l9.debt-defense/v1",
            "pack_id": pack_id,
            "version": version,
            "corpus_snapshot": verification["source_snapshot_id"],
            "analysis_run": verification["analysis_run_id"],
            "compilation_id": verification["compilation_id"],
            "compiler_version": compiler_manifest["compiler_version"],
            "taxonomy_version": taxonomy_version,
            "SDK_contract_version": sdk_contract_version,
            "compatibility": compatibility,
            "rules": rules,
            "checksums": dict(sorted(checksums.items())),
            "signature_metadata": {
                "required": True,
                "algorithm": "Ed25519",
                "signed_value": "archive_sha256",
            },
            "limitations": sorted(set(compiler_manifest.get("limitations", []))),
        }
        pack_bytes = canonical_json(pack) + b"\n"
        (temporary / "defense-pack.json").write_bytes(pack_bytes)
        checksums["defense-pack.json"] = sha256_bytes(pack_bytes)
        checksums_document = {
            "schema_version": "l9.defense-checksums/v1",
            "files": dict(sorted(checksums.items())),
        }
        (temporary / "checksums.json").write_bytes(
            canonical_json(checksums_document) + b"\n"
        )
        members = [
            Path("defense-pack.json"),
            Path("compatibility.json"),
            Path("checksums.json"),
            *[Path(rule["source_path"]) for rule in rules],
        ]
        archive_name = f"l9-debt-defense-{version}-{pack_id[5:17]}.tar.gz"
        archive_path = temporary / archive_name
        build_deterministic_archive(
            source_root=temporary,
            members=members,
            destination=archive_path,
        )
        archive_sha256 = sha256_file(archive_path)
        destination = output_root / pack_id
        if destination.exists():
            existing_archive = destination / archive_name
            if (
                not existing_archive.is_file()
                or sha256_file(existing_archive) != archive_sha256
            ):
                raise PublicationGateError("immutable pack identity collision")
            shutil.rmtree(temporary)
        else:
            os.replace(temporary, destination)
        return {
            "schema_version": "l9.defense-pack-build-result/v1",
            "pack_id": pack_id,
            "pack_version": version,
            "pack_path": destination.as_posix(),
            "archive_path": (destination / archive_name).as_posix(),
            "archive_name": archive_name,
            "archive_sha256": archive_sha256,
            "rule_count": len(rules),
            "corpus_snapshot": verification["source_snapshot_id"],
            "analysis_run": verification["analysis_run_id"],
            "compilation_id": verification["compilation_id"],
        }
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
