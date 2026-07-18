from __future__ import annotations

import json
import tarfile
from pathlib import Path
from typing import Any

from l9_debt_intelligence.snapshots.hashing import (
    sha256_bytes,
    sha256_file,
)

from .crypto import verify_digest
from .errors import PublicationVerificationError

PROHIBITED_MEMBER_TOKENS = (
    "..",
    "/home/",
    "/Users/",
    "\\\\Users\\\\",
    "corpus-record",
    "raw-log",
)


def verify_publication(
    *,
    publication_manifest_path: Path,
    archive_path: Path,
) -> dict[str, Any]:
    manifest = json.loads(publication_manifest_path.read_text(encoding="utf-8"))
    archive_sha256 = sha256_file(archive_path)
    if archive_sha256 != manifest["archive_sha256"]:
        raise PublicationVerificationError("published archive checksum mismatch")
    verify_digest(
        digest_hex=archive_sha256,
        signature=manifest["signature"],
        public_key=manifest["public_key"],
    )
    with tarfile.open(archive_path, mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            name = member.name
            if member.isdir():
                continue
            if name.startswith("/") or any(
                token in name for token in PROHIBITED_MEMBER_TOKENS
            ):
                raise PublicationVerificationError(f"unsafe archive member: {name}")
            if member.uid != 0 or member.gid != 0:
                raise PublicationVerificationError(
                    f"non-deterministic ownership: {name}"
                )
            if member.mtime != 0:
                raise PublicationVerificationError(
                    f"non-deterministic timestamp: {name}"
                )
        required = {
            "defense-pack.json",
            "compatibility.json",
            "checksums.json",
        }
        names = {member.name for member in members}
        if not required.issubset(names):
            raise PublicationVerificationError("archive is missing required metadata")
        pack_member = archive.extractfile("defense-pack.json")
        checksums_member = archive.extractfile("checksums.json")
        if pack_member is None or checksums_member is None:
            raise PublicationVerificationError("archive metadata could not be read")
        pack = json.loads(pack_member.read())
        checksums = json.loads(checksums_member.read())
        if pack["pack_id"] != manifest["pack_id"]:
            raise PublicationVerificationError(
                "pack identity does not match publication manifest"
            )
        for relative, expected in checksums["files"].items():
            extracted = archive.extractfile(relative)
            if extracted is None:
                raise PublicationVerificationError(
                    f"missing checksummed member: {relative}"
                )
            actual = sha256_bytes(extracted.read())
            if actual != expected:
                raise PublicationVerificationError(
                    f"member checksum mismatch: {relative}"
                )
        for rule in pack["rules"]:
            if rule["score"] < 4.0:
                raise PublicationVerificationError(
                    "pack contains a rule below promotion threshold"
                )
            if rule["lineage"]["corpus_snapshot"] != pack["corpus_snapshot"]:
                raise PublicationVerificationError("rule corpus lineage mismatch")
    failed_gates = [
        key for key, value in manifest["publication_gates"].items() if value is not True
    ]
    if failed_gates:
        raise PublicationVerificationError(
            "publication gates failed: " + ", ".join(sorted(failed_gates))
        )
    return {
        "schema_version": "l9.defense-publication-verification/v1",
        "status": "valid",
        "pack_id": manifest["pack_id"],
        "pack_version": manifest["pack_version"],
        "archive_sha256": archive_sha256,
        "signature_algorithm": manifest["signature_algorithm"],
        "channel": manifest["channel"],
        "rule_count": len(pack["rules"]),
    }
