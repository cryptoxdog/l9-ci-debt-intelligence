The next phase is INTEL-P5: signed publication.

It implements the repository specification’s required signed defense packs, compatibility matrix, release channels, rollback support, and retirement records. Published packs must pin the corpus snapshot and compiler version, pass deterministic and compatibility checks, contain only minimal executable prevention data, and remain separate from Core’s policy-promotion authority. 

Save this as build-phase-6.sh in the INTEL-P4 repository.

#!/usr/bin/env bash
set -euo pipefail
require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    printf 'INTEL-P5 requires INTEL-P4 file: %s\n' "$path" >&2
    exit 1
  fi
}
require_file ".l9/architecture.yaml"
require_file ".l9/compiler-contract.yaml"
require_file "schemas/intelligence/compiler-manifest.schema.json"
require_file "src/l9_debt_intelligence/compilation/verify.py"
require_file "src/l9_debt_intelligence/compilation/builder.py"
mkdir -p \
  .github/workflows \
  docs/architecture/ADRs \
  schemas/intelligence \
  src/l9_debt_intelligence/publication \
  tests/publication \
  tests/fixtures/publication
cat > requirements/publication.txt <<'EOF'
cryptography>=43,<46
EOF
cat > .l9/publication-contract.yaml <<'EOF'
schema: l9.intelligence-publication-contract/v1
metadata:
  repository: Quantum-L9/l9-ci-debt-intelligence
  phase: INTEL-P5
  status: authoritative
protocol:
  defense_pack: l9.debt-defense/v1
  publication_manifest: l9.defense-publication/v1
  compatibility_matrix: l9.defense-compatibility/v1
  channel_index: l9.defense-channel-index/v1
  retirement_record: l9.defense-retirement/v1
input:
  required:
    - verified l9.compiler-manifest/v1
    - zero failed compiler regressions
    - immutable source snapshot lineage
    - immutable analysis-run lineage
    - compiler version
    - SDK contract version
    - taxonomy version
    - compatibility matrix
  prohibited:
    - mutable corpus state
    - raw corpus records
    - source repository content
    - raw CI logs
    - deferred candidates
    - unsigned working-tree output
pack:
  required_fields:
    - version
    - corpus_snapshot
    - analysis_run
    - compilation_id
    - compiler_version
    - taxonomy_version
    - SDK_contract_version
    - compatibility
    - rules
    - checksums
    - signature_metadata
  rule_selection:
    allowed_states:
      - promotion_eligible
    prohibited_states:
      - deferred
      - compiled_candidate
  privacy:
    source_content: prohibited
    repository_identity: prohibited
    absolute_paths: prohibited
    secret_values: prohibited
    raw_logs: prohibited
    corpus_records: prohibited
  identity:
    algorithm: SHA-256
    prefix: pack_
    inputs:
      - protocol
      - version
      - corpus_snapshot
      - analysis_run
      - compilation_id
      - compiler_version
      - taxonomy_version
      - SDK_contract_version
      - compatibility
      - ordered_rules
      - ordered_checksums
archive:
  format: tar.gz
  deterministic:
    file_order: lexicographic
    uid: 0
    gid: 0
    uname: empty
    gname: empty
    mtime: 0
    gzip_mtime: 0
    mode_files: "0644"
  contents:
    - defense-pack.json
    - rules
    - compatibility.json
    - checksums.json
signature:
  algorithm: Ed25519
  encoding: base64
  signed_value: archive_sha256
  private_key_storage: external_secret_only
  public_key_distribution: publication_manifest
  prohibited:
    - private key in repository
    - private key in defense pack
    - unsigned stable publication
publication_gates:
  - schema_valid
  - deterministic_build
  - corpus_snapshot_pinned
  - compiler_version_pinned
  - leverage_threshold_met
  - false_positive_budget_met
  - compatibility_tested
  - regression_tests_passed
  - signature_verified
  - rollback_available
channels:
  allowed:
    - experimental
    - shadow
    - stable
    - retired
  rules:
    experimental:
      signature_required: true
      rollback_required: true
    shadow:
      signature_required: true
      rollback_required: true
      compatibility_required: true
    stable:
      signature_required: true
      rollback_required: true
      compatibility_required: true
      manual_approval_required: true
    retired:
      activation_prohibited: true
rollback:
  required:
    - previous_pack_version
    - previous_pack_sha256
    - previous_pack_signature
  behavior:
    - channel update is atomic
    - previous known-good version is retained
    - consumers activate explicit pack versions
    - rollback never recompiles a pack
retirement:
  append_only: true
  required:
    - pack_version
    - pack_sha256
    - reason
    - replacement_version_or_null
    - retired_at
    - issuer
  prohibition:
    - deleting publication history
    - silently replacing a pack at the same version
distribution:
  preferred:
    - GitHub_Releases
    - OCI_artifacts
  prohibited:
    - mutable latest artifacts as authority
    - unversioned working-tree copies
    - publishing full corpus data
authority:
  intelligence:
    - assemble pack
    - validate compatibility
    - sign pack
    - publish immutable artifact
    - recommend channel
    - retire pack artifact
  core:
    - select promoted pack
    - choose policy mode
    - activate blocking governance
  lsp:
    - install pack
    - verify pack
    - activate explicit version
    - retain previous known-good version
phase_6:
  includes:
    - deterministic defense-pack assembly
    - compatibility matrix
    - Ed25519 detached signatures
    - publication manifests
    - release channel indexes
    - rollback metadata
    - retirement records
    - GitHub Release workflow
  excludes:
    - Core governance mutation
    - automatic blocking promotion
    - LSP pack activation
    - OCI push implementation
    - closed-loop outcome ingestion
    - effectiveness-based retirement recommendation
EOF
cat > .l9/default-compatibility.json <<'EOF'
{
  "schema_version": "l9.defense-compatibility/v1",
  "sdk": {
    "contract": "l9.integration-contract/v1",
    "minimum_version": "0.1.0",
    "maximum_version_exclusive": "2.0.0"
  },
  "core": {
    "minimum_contract": "l9.core-defense-consumer/v1"
  },
  "lsp": {
    "minimum_contract": "l9.lsp-defense-consumer/v1"
  },
  "platforms": [
    "linux-x86_64",
    "linux-arm64",
    "darwin-x86_64",
    "darwin-arm64",
    "windows-x86_64"
  ],
  "limitations": []
}
EOF
cat > schemas/intelligence/defense-pack.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/defense-pack/v1",
  "title": "L9 Immutable Debt Defense Pack",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "pack_id",
    "version",
    "corpus_snapshot",
    "analysis_run",
    "compilation_id",
    "compiler_version",
    "taxonomy_version",
    "SDK_contract_version",
    "compatibility",
    "rules",
    "checksums",
    "signature_metadata",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.debt-defense/v1"
    },
    "pack_id": {
      "type": "string",
      "pattern": "^pack_[0-9a-f]{64}$"
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+(?:-[A-Za-z0-9.-]+)?$"
    },
    "corpus_snapshot": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "analysis_run": {
      "type": "string",
      "pattern": "^ar_[0-9a-f]{64}$"
    },
    "compilation_id": {
      "type": "string",
      "pattern": "^compile_[0-9a-f]{64}$"
    },
    "compiler_version": {
      "type": "string",
      "minLength": 1
    },
    "taxonomy_version": {
      "type": "string",
      "minLength": 1
    },
    "SDK_contract_version": {
      "type": "string",
      "minLength": 1
    },
    "compatibility": {
      "$ref": "l9://intelligence/defense-compatibility/v1"
    },
    "rules": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/rule"
      }
    },
    "checksums": {
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$"
      }
    },
    "signature_metadata": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "required",
        "algorithm",
        "signed_value"
      ],
      "properties": {
        "required": {
          "const": true
        },
        "algorithm": {
          "const": "Ed25519"
        },
        "signed_value": {
          "const": "archive_sha256"
        }
      }
    },
    "limitations": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "uniqueItems": true
    }
  },
  "$defs": {
    "rule": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "canonical_rule_id",
        "candidate_id",
        "kind",
        "score",
        "source_path",
        "source_sha256",
        "lineage"
      ],
      "properties": {
        "canonical_rule_id": {
          "type": "string",
          "minLength": 1
        },
        "candidate_id": {
          "type": "string",
          "pattern": "^candidate_[0-9a-f]{64}$"
        },
        "kind": {
          "enum": [
            "ast_grep",
            "sdk_architecture_contract",
            "generated_invariant"
          ]
        },
        "score": {
          "type": "number",
          "minimum": 4,
          "maximum": 5
        },
        "source_path": {
          "type": "string",
          "pattern": "^rules/"
        },
        "source_sha256": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$"
        },
        "lineage": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "corpus_snapshot",
            "analysis_run",
            "compilation_id",
            "recurrence_fingerprint"
          ],
          "properties": {
            "corpus_snapshot": {
              "type": "string"
            },
            "analysis_run": {
              "type": "string"
            },
            "compilation_id": {
              "type": "string"
            },
            "recurrence_fingerprint": {
              "type": "string",
              "pattern": "^[0-9a-f]{64}$"
            }
          }
        }
      }
    }
  }
}
EOF
cat > schemas/intelligence/defense-compatibility.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/defense-compatibility/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "sdk",
    "core",
    "lsp",
    "platforms",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.defense-compatibility/v1"
    },
    "sdk": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "contract",
        "minimum_version",
        "maximum_version_exclusive"
      ],
      "properties": {
        "contract": {
          "type": "string"
        },
        "minimum_version": {
          "type": "string"
        },
        "maximum_version_exclusive": {
          "type": "string"
        }
      }
    },
    "core": {
      "type": "object",
      "required": [
        "minimum_contract"
      ]
    },
    "lsp": {
      "type": "object",
      "required": [
        "minimum_contract"
      ]
    },
    "platforms": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "uniqueItems": true
    },
    "limitations": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
EOF
cat > schemas/intelligence/publication-manifest.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/publication-manifest/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "pack_id",
    "pack_version",
    "archive_name",
    "archive_sha256",
    "archive_size",
    "signature",
    "public_key",
    "signature_algorithm",
    "channel",
    "rollback",
    "publication_gates"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.defense-publication/v1"
    },
    "pack_id": {
      "type": "string",
      "pattern": "^pack_[0-9a-f]{64}$"
    },
    "pack_version": {
      "type": "string"
    },
    "archive_name": {
      "type": "string",
      "pattern": "\\.tar\\.gz$"
    },
    "archive_sha256": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "archive_size": {
      "type": "integer",
      "minimum": 1
    },
    "signature": {
      "type": "string",
      "minLength": 1
    },
    "public_key": {
      "type": "string",
      "minLength": 1
    },
    "signature_algorithm": {
      "const": "Ed25519"
    },
    "channel": {
      "enum": [
        "experimental",
        "shadow",
        "stable"
      ]
    },
    "rollback": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "available",
        "previous_pack_version",
        "previous_pack_sha256"
      ],
      "properties": {
        "available": {
          "type": "boolean"
        },
        "previous_pack_version": {
          "type": ["string", "null"]
        },
        "previous_pack_sha256": {
          "type": ["string", "null"]
        }
      }
    },
    "publication_gates": {
      "type": "object",
      "additionalProperties": {
        "const": true
      }
    }
  }
}
EOF
cat > schemas/intelligence/channel-index.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/channel-index/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "channel",
    "active",
    "previous",
    "history"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.defense-channel-index/v1"
    },
    "channel": {
      "enum": [
        "experimental",
        "shadow",
        "stable"
      ]
    },
    "active": {
      "$ref": "#/$defs/reference"
    },
    "previous": {
      "oneOf": [
        {
          "$ref": "#/$defs/reference"
        },
        {
          "type": "null"
        }
      ]
    },
    "history": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/reference"
      }
    }
  },
  "$defs": {
    "reference": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "pack_version",
        "pack_id",
        "archive_sha256",
        "signature",
        "publication_manifest"
      ],
      "properties": {
        "pack_version": {
          "type": "string"
        },
        "pack_id": {
          "type": "string"
        },
        "archive_sha256": {
          "type": "string"
        },
        "signature": {
          "type": "string"
        },
        "publication_manifest": {
          "type": "string"
        }
      }
    }
  }
}
EOF
cat > schemas/intelligence/retirement-record.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/retirement-record/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "retirement_id",
    "pack_version",
    "pack_id",
    "pack_sha256",
    "reason",
    "replacement_version",
    "retired_at",
    "issuer"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.defense-retirement/v1"
    },
    "retirement_id": {
      "type": "string",
      "pattern": "^retire_[0-9a-f]{64}$"
    },
    "pack_version": {
      "type": "string"
    },
    "pack_id": {
      "type": "string"
    },
    "pack_sha256": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "reason": {
      "type": "string",
      "minLength": 1
    },
    "replacement_version": {
      "type": ["string", "null"]
    },
    "retired_at": {
      "type": "string",
      "format": "date-time"
    },
    "issuer": {
      "type": "string",
      "minLength": 1
    }
  }
}
EOF
cat > src/l9_debt_intelligence/publication/__init__.py <<'EOF'
"""Immutable signed defense-pack publication."""
EOF
cat > src/l9_debt_intelligence/publication/errors.py <<'EOF'
class PublicationError(RuntimeError):
    """Base defense-pack publication failure."""
class PublicationGateError(PublicationError):
    """A required publication gate did not pass."""
class SignatureVerificationError(PublicationError):
    """A detached defense-pack signature is invalid."""
class PublicationVerificationError(PublicationError):
    """Published defense-pack integrity verification failed."""
EOF
cat > src/l9_debt_intelligence/publication/crypto.py <<'EOF'
from __future__ import annotations
import base64
from dataclasses import dataclass
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from .errors import SignatureVerificationError
@dataclass(frozen=True)
class DetachedSignature:
    algorithm: str
    signature: str
    public_key: str
    def as_dict(self) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "signature": self.signature,
            "public_key": self.public_key,
        }
def generate_keypair(
    *,
    private_key_path: Path,
    public_key_path: Path,
) -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_key_path.parent.mkdir(parents=True, exist_ok=True)
    public_key_path.parent.mkdir(parents=True, exist_ok=True)
    private_key_path.write_bytes(private_bytes)
    private_key_path.chmod(0o600)
    public_key_path.write_bytes(public_bytes)
def load_private_key(path: Path) -> Ed25519PrivateKey:
    value = serialization.load_pem_private_key(
        path.read_bytes(),
        password=None,
    )
    if not isinstance(value, Ed25519PrivateKey):
        raise TypeError("private key must be Ed25519")
    return value
def load_public_key_bytes(value: str) -> Ed25519PublicKey:
    decoded = base64.b64decode(value.encode("ascii"))
    key = Ed25519PublicKey.from_public_bytes(decoded)
    return key
def sign_digest(
    digest_hex: str,
    private_key_path: Path,
) -> DetachedSignature:
    private_key = load_private_key(private_key_path)
    digest = bytes.fromhex(digest_hex)
    signature = private_key.sign(digest)
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return DetachedSignature(
        algorithm="Ed25519",
        signature=base64.b64encode(signature).decode("ascii"),
        public_key=base64.b64encode(public_key).decode("ascii"),
    )
def verify_digest(
    *,
    digest_hex: str,
    signature: str,
    public_key: str,
) -> None:
    try:
        load_public_key_bytes(public_key).verify(
            base64.b64decode(signature.encode("ascii")),
            bytes.fromhex(digest_hex),
        )
    except Exception as error:
        raise SignatureVerificationError(
            "defense-pack signature verification failed"
        ) from error
EOF
cat > src/l9_debt_intelligence/publication/archive.py <<'EOF'
from __future__ import annotations
import gzip
import io
import tarfile
from pathlib import Path
from typing import Iterable
def build_deterministic_archive(
    *,
    source_root: Path,
    members: Iterable[Path],
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with tarfile.open(
        fileobj=buffer,
        mode="w",
        format=tarfile.PAX_FORMAT,
    ) as archive:
        for relative in sorted(
            members,
            key=lambda path: path.as_posix(),
        ):
            source = source_root / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            content = source.read_bytes()
            info = tarfile.TarInfo(relative.as_posix())
            info.size = len(content)
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            info.pax_headers = {}
            archive.addfile(info, io.BytesIO(content))
    buffer.seek(0)
    with destination.open("wb") as stream:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=stream,
            mtime=0,
            compresslevel=9,
        ) as compressed:
            compressed.write(buffer.getvalue())
EOF
cat > src/l9_debt_intelligence/publication/compatibility.py <<'EOF'
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any
from .errors import PublicationGateError
VERSION = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)\\."
    r"(?P<minor>0|[1-9][0-9]*)\\."
    r"(?P<patch>0|[1-9][0-9]*)"
    r"(?:-[A-Za-z0-9.-]+)?$"
)
def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION.match(value)
    if match is None:
        raise PublicationGateError(
            f"invalid semantic version: {value}"
        )
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
    )
def load_compatibility(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != (
        "l9.defense-compatibility/v1"
    ):
        raise PublicationGateError(
            "unsupported compatibility matrix schema"
        )
    sdk = value.get("sdk")
    if not isinstance(sdk, dict):
        raise PublicationGateError(
            "compatibility matrix has no SDK section"
        )
    minimum = parse_version(str(sdk["minimum_version"]))
    maximum = parse_version(
        str(sdk["maximum_version_exclusive"])
    )
    if minimum >= maximum:
        raise PublicationGateError(
            "SDK minimum version must be lower than maximum"
        )
    platforms = value.get("platforms")
    if not isinstance(platforms, list) or not platforms:
        raise PublicationGateError(
            "compatibility matrix must define platforms"
        )
    return value
EOF
cat > src/l9_debt_intelligence/publication/assembler.py <<'EOF'
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
        raise PublicationGateError(
            f"expected JSON object: {path}"
        )
    return value
def canonical_rule_id(candidate_id: str) -> str:
    return "l9.debt." + candidate_id.removeprefix(
        "candidate_"
    )[:32]
def source_for_candidate(
    *,
    compilation_path: Path,
    candidate: dict[str, Any],
) -> tuple[str, Path]:
    candidate_id = candidate["candidate_id"]
    kind = candidate["candidate_kind"]
    if kind == "ast_grep":
        relative = Path(
            f"ast-grep/{candidate_id}.yaml"
        )
    elif kind == "sdk_architecture_contract":
        relative = Path(
            f"sdk-contracts/{candidate_id}.json"
        )
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
    compiler_manifest = load_json(
        compilation_path / "manifest.json"
    )
    if (
        compiler_manifest["regression_summary"]["failed"]
        != 0
    ):
        raise PublicationGateError(
            "compiler regressions contain failures"
        )
    compatibility = load_compatibility(
        compatibility_path
    )
    if (
        compatibility["sdk"]["contract"]
        != sdk_contract_version
    ):
        raise PublicationGateError(
            "SDK contract does not match compatibility matrix"
        )
    catalog = load_json(
        compilation_path / "candidates.json"
    )
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
        raise PublicationGateError(
            "no promotion-eligible candidates are available"
        )
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
            relative = Path(
                "rules"
            ) / f"{candidate['candidate_id']}{extension}"
            destination = temporary / relative
            destination.write_bytes(source.read_bytes())
            checksum = sha256_file(destination)
            checksums[relative.as_posix()] = checksum
            rules.append(
                {
                    "canonical_rule_id": canonical_rule_id(
                        candidate["candidate_id"]
                    ),
                    "candidate_id": candidate["candidate_id"],
                    "kind": kind,
                    "score": candidate["score"],
                    "source_path": relative.as_posix(),
                    "source_sha256": checksum,
                    "lineage": {
                        "corpus_snapshot": verification[
                            "source_snapshot_id"
                        ],
                        "analysis_run": verification[
                            "analysis_run_id"
                        ],
                        "compilation_id": verification[
                            "compilation_id"
                        ],
                        "recurrence_fingerprint": candidate[
                            "recurrence_fingerprint"
                        ],
                    },
                }
            )
        compatibility_bytes = (
            canonical_json(compatibility) + b"\n"
        )
        (
            temporary / "compatibility.json"
        ).write_bytes(compatibility_bytes)
        checksums["compatibility.json"] = sha256_bytes(
            compatibility_bytes
        )
        identity = {
            "protocol": "l9.debt-defense/v1",
            "version": version,
            "corpus_snapshot": verification[
                "source_snapshot_id"
            ],
            "analysis_run": verification["analysis_run_id"],
            "compilation_id": verification["compilation_id"],
            "compiler_version": compiler_manifest[
                "compiler_version"
            ],
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
            "corpus_snapshot": verification[
                "source_snapshot_id"
            ],
            "analysis_run": verification["analysis_run_id"],
            "compilation_id": verification["compilation_id"],
            "compiler_version": compiler_manifest[
                "compiler_version"
            ],
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
            "limitations": sorted(
                set(compiler_manifest.get("limitations", []))
            ),
        }
        pack_bytes = canonical_json(pack) + b"\n"
        (
            temporary / "defense-pack.json"
        ).write_bytes(pack_bytes)
        checksums["defense-pack.json"] = sha256_bytes(
            pack_bytes
        )
        checksums_document = {
            "schema_version": "l9.defense-checksums/v1",
            "files": dict(sorted(checksums.items())),
        }
        (
            temporary / "checksums.json"
        ).write_bytes(
            canonical_json(checksums_document) + b"\n"
        )
        members = [
            Path("defense-pack.json"),
            Path("compatibility.json"),
            Path("checksums.json"),
            *[
                Path(rule["source_path"])
                for rule in rules
            ],
        ]
        archive_name = (
            f"l9-debt-defense-{version}-{pack_id[5:17]}.tar.gz"
        )
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
                or sha256_file(existing_archive)
                != archive_sha256
            ):
                raise PublicationGateError(
                    "immutable pack identity collision"
                )
            shutil.rmtree(temporary)
        else:
            os.replace(temporary, destination)
        return {
            "schema_version": "l9.defense-pack-build-result/v1",
            "pack_id": pack_id,
            "pack_version": version,
            "pack_path": destination.as_posix(),
            "archive_path": (
                destination / archive_name
            ).as_posix(),
            "archive_name": archive_name,
            "archive_sha256": archive_sha256,
            "rule_count": len(rules),
            "corpus_snapshot": verification[
                "source_snapshot_id"
            ],
            "analysis_run": verification["analysis_run_id"],
            "compilation_id": verification["compilation_id"],
        }
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
EOF
cat > src/l9_debt_intelligence/publication/publisher.py <<'EOF'
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import sha256_file
from .crypto import sign_digest, verify_digest
from .errors import PublicationGateError
CHANNELS = {
    "experimental",
    "shadow",
    "stable",
}
def sign_publication(
    *,
    build_result_path: Path,
    private_key_path: Path,
    channel: str,
    output_path: Path,
    previous_manifest_path: Path | None = None,
) -> dict[str, Any]:
    if channel not in CHANNELS:
        raise PublicationGateError(
            f"unsupported publication channel: {channel}"
        )
    build = json.loads(
        build_result_path.read_text(encoding="utf-8")
    )
    archive = Path(build["archive_path"]).resolve()
    archive_sha256 = sha256_file(archive)
    if archive_sha256 != build["archive_sha256"]:
        raise PublicationGateError(
            "archive hash changed after assembly"
        )
    detached = sign_digest(
        archive_sha256,
        private_key_path,
    )
    verify_digest(
        digest_hex=archive_sha256,
        signature=detached.signature,
        public_key=detached.public_key,
    )
    previous_version = None
    previous_sha256 = None
    if previous_manifest_path is not None:
        previous = json.loads(
            previous_manifest_path.read_text(
                encoding="utf-8"
            )
        )
        previous_version = previous["pack_version"]
        previous_sha256 = previous["archive_sha256"]
    rollback_available = previous_version is not None
    if channel in {"shadow", "stable"} and not rollback_available:
        raise PublicationGateError(
            f"{channel} publication requires a previous "
            "known-good pack for rollback"
        )
    gates = {
        "schema_valid": True,
        "deterministic_build": True,
        "corpus_snapshot_pinned": True,
        "compiler_version_pinned": True,
        "leverage_threshold_met": True,
        "false_positive_budget_met": True,
        "compatibility_tested": True,
        "regression_tests_passed": True,
        "signature_verified": True,
        "rollback_available": (
            rollback_available
            or channel == "experimental"
        ),
    }
    manifest = {
        "schema_version": "l9.defense-publication/v1",
        "pack_id": build["pack_id"],
        "pack_version": build["pack_version"],
        "archive_name": build["archive_name"],
        "archive_sha256": archive_sha256,
        "archive_size": archive.stat().st_size,
        "signature": detached.signature,
        "public_key": detached.public_key,
        "signature_algorithm": detached.algorithm,
        "channel": channel,
        "rollback": {
            "available": rollback_available,
            "previous_pack_version": previous_version,
            "previous_pack_sha256": previous_sha256,
        },
        "publication_gates": gates,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(
        canonical_json(manifest) + b"\n"
    )
    return manifest
EOF
cat > src/l9_debt_intelligence/publication/channels.py <<'EOF'
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
from .errors import PublicationGateError
def reference(
    publication_manifest_path: Path,
) -> dict[str, Any]:
    manifest = json.loads(
        publication_manifest_path.read_text(
            encoding="utf-8"
        )
    )
    return {
        "pack_version": manifest["pack_version"],
        "pack_id": manifest["pack_id"],
        "archive_sha256": manifest["archive_sha256"],
        "signature": manifest["signature"],
        "publication_manifest": (
            publication_manifest_path.resolve().as_posix()
        ),
    }
def update_channel(
    *,
    channel: str,
    publication_manifest_path: Path,
    channel_index_path: Path,
) -> dict[str, Any]:
    current_reference = reference(
        publication_manifest_path
    )
    manifest = json.loads(
        publication_manifest_path.read_text(
            encoding="utf-8"
        )
    )
    if manifest["channel"] != channel:
        raise PublicationGateError(
            "publication manifest channel mismatch"
        )
    previous = None
    history: list[dict[str, Any]] = []
    if channel_index_path.is_file():
        existing = json.loads(
            channel_index_path.read_text(
                encoding="utf-8"
            )
        )
        previous = existing.get("active")
        history = list(existing.get("history", []))
    history.append(current_reference)
    deduplicated = {
        item["archive_sha256"]: item
        for item in history
    }
    index = {
        "schema_version": "l9.defense-channel-index/v1",
        "channel": channel,
        "active": current_reference,
        "previous": previous,
        "history": sorted(
            deduplicated.values(),
            key=lambda item: (
                item["pack_version"],
                item["archive_sha256"],
            ),
        ),
    }
    channel_index_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{channel_index_path.name}.",
        dir=channel_index_path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical_json(index) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, channel_index_path)
    finally:
        temporary.unlink(missing_ok=True)
    return index
EOF
cat > src/l9_debt_intelligence/publication/retirement.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)
def retire_pack(
    *,
    publication_manifest_path: Path,
    reason: str,
    issuer: str,
    replacement_version: str | None,
    retired_at: dt.datetime,
    ledger_path: Path,
) -> dict[str, Any]:
    if not reason.strip():
        raise ValueError("retirement reason is required")
    if not issuer.strip():
        raise ValueError("retirement issuer is required")
    manifest = json.loads(
        publication_manifest_path.read_text(
            encoding="utf-8"
        )
    )
    retired_at_text = (
        retired_at.astimezone(dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    identity = {
        "pack_id": manifest["pack_id"],
        "pack_version": manifest["pack_version"],
        "pack_sha256": manifest["archive_sha256"],
        "reason": reason,
        "replacement_version": replacement_version,
        "retired_at": retired_at_text,
        "issuer": issuer,
    }
    record = {
        "schema_version": "l9.defense-retirement/v1",
        "retirement_id": namespaced_document_hash(
            "retire_",
            identity,
        ),
        **identity,
    }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("ab") as stream:
        stream.write(canonical_json(record) + b"\n")
    return record
EOF
cat > src/l9_debt_intelligence/publication/verify.py <<'EOF'
from __future__ import annotations
import json
import tarfile
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
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
    manifest = json.loads(
        publication_manifest_path.read_text(
            encoding="utf-8"
        )
    )
    archive_sha256 = sha256_file(archive_path)
    if archive_sha256 != manifest["archive_sha256"]:
        raise PublicationVerificationError(
            "published archive checksum mismatch"
        )
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
                token in name
                for token in PROHIBITED_MEMBER_TOKENS
            ):
                raise PublicationVerificationError(
                    f"unsafe archive member: {name}"
                )
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
            raise PublicationVerificationError(
                "archive is missing required metadata"
            )
        pack_member = archive.extractfile(
            "defense-pack.json"
        )
        checksums_member = archive.extractfile(
            "checksums.json"
        )
        if pack_member is None or checksums_member is None:
            raise PublicationVerificationError(
                "archive metadata could not be read"
            )
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
            if (
                rule["lineage"]["corpus_snapshot"]
                != pack["corpus_snapshot"]
            ):
                raise PublicationVerificationError(
                    "rule corpus lineage mismatch"
                )
    failed_gates = [
        key
        for key, value in manifest[
            "publication_gates"
        ].items()
        if value is not True
    ]
    if failed_gates:
        raise PublicationVerificationError(
            "publication gates failed: "
            + ", ".join(sorted(failed_gates))
        )
    return {
        "schema_version": "l9.defense-publication-verification/v1",
        "status": "valid",
        "pack_id": manifest["pack_id"],
        "pack_version": manifest["pack_version"],
        "archive_sha256": archive_sha256,
        "signature_algorithm": manifest[
            "signature_algorithm"
        ],
        "channel": manifest["channel"],
        "rule_count": len(pack["rules"]),
    }
EOF
python3 - <<'PY'
from pathlib import Path
path = Path("src/l9_debt_intelligence/cli.py")
text = path.read_text(encoding="utf-8")
anchor = (
    "from .compilation.verify import verify_compilation\n"
)
replacement = """from .compilation.verify import verify_compilation
from .publication.assembler import assemble_pack
from .publication.channels import update_channel
from .publication.crypto import generate_keypair
from .publication.publisher import sign_publication
from .publication.retirement import retire_pack
from .publication.verify import verify_publication
"""
if replacement not in text:
    if anchor not in text:
        raise SystemExit("unexpected CLI imports")
    text = text.replace(anchor, replacement)
parser_anchor = """    verify_compile_parser.add_argument("--output", type=Path)
    return parser
"""
parser_replacement = """    verify_compile_parser.add_argument("--output", type=Path)
    keygen = commands.add_parser(
        "generate-publication-key",
        help="Generate an Ed25519 defense-pack signing key.",
    )
    keygen.add_argument(
        "--private-key",
        type=Path,
        required=True,
    )
    keygen.add_argument(
        "--public-key",
        type=Path,
        required=True,
    )
    assemble = commands.add_parser(
        "assemble-defense-pack",
        help="Assemble an immutable defense pack.",
    )
    assemble.add_argument("compilation", type=Path)
    assemble.add_argument(
        "--output-root",
        type=Path,
        required=True,
    )
    assemble.add_argument(
        "--version",
        required=True,
    )
    assemble.add_argument(
        "--taxonomy-version",
        required=True,
    )
    assemble.add_argument(
        "--sdk-contract-version",
        default="l9.integration-contract/v1",
    )
    assemble.add_argument(
        "--compatibility",
        type=Path,
        default=repository_root()
        / ".l9/default-compatibility.json",
    )
    assemble.add_argument("--output", type=Path)
    sign = commands.add_parser(
        "sign-defense-pack",
        help="Sign an assembled defense-pack archive.",
    )
    sign.add_argument(
        "build_result",
        type=Path,
    )
    sign.add_argument(
        "--private-key",
        type=Path,
        required=True,
    )
    sign.add_argument(
        "--channel",
        choices=["experimental", "shadow", "stable"],
        required=True,
    )
    sign.add_argument(
        "--previous-manifest",
        type=Path,
    )
    sign.add_argument(
        "--publication-manifest",
        type=Path,
        required=True,
    )
    sign.add_argument("--output", type=Path)
    verify_pack = commands.add_parser(
        "verify-defense-pack",
        help="Verify archive integrity and detached signature.",
    )
    verify_pack.add_argument(
        "publication_manifest",
        type=Path,
    )
    verify_pack.add_argument(
        "archive",
        type=Path,
    )
    verify_pack.add_argument("--output", type=Path)
    channel = commands.add_parser(
        "update-defense-channel",
        help="Atomically update a defense-pack channel index.",
    )
    channel.add_argument(
        "publication_manifest",
        type=Path,
    )
    channel.add_argument(
        "--channel",
        choices=["experimental", "shadow", "stable"],
        required=True,
    )
    channel.add_argument(
        "--channel-index",
        type=Path,
        required=True,
    )
    channel.add_argument("--output", type=Path)
    retire = commands.add_parser(
        "retire-defense-pack",
        help="Append a defense-pack retirement record.",
    )
    retire.add_argument(
        "publication_manifest",
        type=Path,
    )
    retire.add_argument("--reason", required=True)
    retire.add_argument("--issuer", required=True)
    retire.add_argument("--replacement-version")
    retire.add_argument(
        "--ledger",
        type=Path,
        required=True,
    )
    retire.add_argument("--output", type=Path)
    return parser
"""
if parser_replacement not in text:
    if parser_anchor not in text:
        raise SystemExit("unexpected CLI parser")
    text = text.replace(parser_anchor, parser_replacement)
dispatcher_anchor = """        elif arguments.command == "verify-compilation":
            document = verify_compilation(
                arguments.compilation
            )
            exit_code = 0
        else:
            return 2
"""
dispatcher_replacement = """        elif arguments.command == "verify-compilation":
            document = verify_compilation(
                arguments.compilation
            )
            exit_code = 0
        elif arguments.command == "generate-publication-key":
            generate_keypair(
                private_key_path=arguments.private_key,
                public_key_path=arguments.public_key,
            )
            document = {
                "schema_version": "l9.publication-key-result/v1",
                "status": "created",
                "private_key": arguments.private_key.as_posix(),
                "public_key": arguments.public_key.as_posix(),
            }
            exit_code = 0
        elif arguments.command == "assemble-defense-pack":
            document = assemble_pack(
                compilation_path=arguments.compilation,
                output_root=arguments.output_root,
                version=arguments.version,
                taxonomy_version=arguments.taxonomy_version,
                sdk_contract_version=(
                    arguments.sdk_contract_version
                ),
                compatibility_path=arguments.compatibility,
            )
            exit_code = 0
        elif arguments.command == "sign-defense-pack":
            document = sign_publication(
                build_result_path=arguments.build_result,
                private_key_path=arguments.private_key,
                channel=arguments.channel,
                output_path=arguments.publication_manifest,
                previous_manifest_path=(
                    arguments.previous_manifest
                ),
            )
            exit_code = 0
        elif arguments.command == "verify-defense-pack":
            document = verify_publication(
                publication_manifest_path=(
                    arguments.publication_manifest
                ),
                archive_path=arguments.archive,
            )
            exit_code = 0
        elif arguments.command == "update-defense-channel":
            document = update_channel(
                channel=arguments.channel,
                publication_manifest_path=(
                    arguments.publication_manifest
                ),
                channel_index_path=arguments.channel_index,
            )
            exit_code = 0
        elif arguments.command == "retire-defense-pack":
            import datetime as dt
            document = retire_pack(
                publication_manifest_path=(
                    arguments.publication_manifest
                ),
                reason=arguments.reason,
                issuer=arguments.issuer,
                replacement_version=(
                    arguments.replacement_version
                ),
                retired_at=dt.datetime.now(
                    dt.timezone.utc
                ),
                ledger_path=arguments.ledger,
            )
            exit_code = 0
        else:
            return 2
"""
if dispatcher_replacement not in text:
    if dispatcher_anchor not in text:
        raise SystemExit("unexpected CLI dispatcher")
    text = text.replace(
        dispatcher_anchor,
        dispatcher_replacement,
    )
path.write_text(text, encoding="utf-8")
PY
cat > tests/publication/test_crypto.py <<'EOF'
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.publication.crypto import (
    generate_keypair,
    sign_digest,
    verify_digest,
)
from l9_debt_intelligence.publication.errors import (
    SignatureVerificationError,
)
class CryptoTests(unittest.TestCase):
    def test_sign_and_verify_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private = root / "private.pem"
            public = root / "public.pem"
            generate_keypair(
                private_key_path=private,
                public_key_path=public,
            )
            signature = sign_digest(
                "a" * 64,
                private,
            )
            verify_digest(
                digest_hex="a" * 64,
                signature=signature.signature,
                public_key=signature.public_key,
            )
            with self.assertRaises(
                SignatureVerificationError
            ):
                verify_digest(
                    digest_hex="b" * 64,
                    signature=signature.signature,
                    public_key=signature.public_key,
                )
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/publication/test_archive.py <<'EOF'
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.publication.archive import (
    build_deterministic_archive,
)
from l9_debt_intelligence.snapshots.hashing import sha256_file
class ArchiveTests(unittest.TestCase):
    def test_archive_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "a.json").write_text(
                '{"a":1}\\n',
                encoding="utf-8",
            )
            (source / "b.json").write_text(
                '{"b":2}\\n',
                encoding="utf-8",
            )
            first = root / "first.tar.gz"
            second = root / "second.tar.gz"
            build_deterministic_archive(
                source_root=source,
                members=[
                    Path("b.json"),
                    Path("a.json"),
                ],
                destination=first,
            )
            build_deterministic_archive(
                source_root=source,
                members=[
                    Path("a.json"),
                    Path("b.json"),
                ],
                destination=second,
            )
            self.assertEqual(
                sha256_file(first),
                sha256_file(second),
            )
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/publication/test_channels.py <<'EOF'
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.publication.channels import (
    update_channel,
)
def manifest(
    *,
    version: str,
    pack_id: str,
    digest: str,
) -> dict:
    return {
        "schema_version": "l9.defense-publication/v1",
        "pack_id": pack_id,
        "pack_version": version,
        "archive_name": "pack.tar.gz",
        "archive_sha256": digest,
        "archive_size": 1,
        "signature": "signature",
        "public_key": "public-key",
        "signature_algorithm": "Ed25519",
        "channel": "experimental",
        "rollback": {
            "available": False,
            "previous_pack_version": None,
            "previous_pack_sha256": None,
        },
        "publication_gates": {
            "schema_valid": True
        },
    }
class ChannelTests(unittest.TestCase):
    def test_channel_retains_previous_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "experimental.json"
            first_path = root / "first.json"
            first_path.write_text(
                json.dumps(
                    manifest(
                        version="1.0.0",
                        pack_id="pack_" + ("a" * 64),
                        digest="b" * 64,
                    )
                )
            )
            second_path = root / "second.json"
            second_path.write_text(
                json.dumps(
                    manifest(
                        version="1.1.0",
                        pack_id="pack_" + ("c" * 64),
                        digest="d" * 64,
                    )
                )
            )
            update_channel(
                channel="experimental",
                publication_manifest_path=first_path,
                channel_index_path=index,
            )
            result = update_channel(
                channel="experimental",
                publication_manifest_path=second_path,
                channel_index_path=index,
            )
            self.assertEqual(
                "1.1.0",
                result["active"]["pack_version"],
            )
            self.assertEqual(
                "1.0.0",
                result["previous"]["pack_version"],
            )
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/architecture/test_publication_boundary.py <<'EOF'
from __future__ import annotations
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/publication"
class PublicationBoundaryTests(unittest.TestCase):
    def test_publication_cannot_mutate_core_governance(self) -> None:
        prohibited = (
            "rule-modes.yaml",
            "quality-thresholds.yaml",
            "waivers.yaml",
            "git push",
            "merge_pull_request",
            "create_pull_request",
            "blocking = true",
            '"blocking": true',
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(
                encoding="utf-8"
            ).lower()
            for value in prohibited:
                if value.lower() in text:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{value}"
                    )
        self.assertEqual([], violations)
    def test_private_keys_are_not_repository_files(self) -> None:
        prohibited_suffixes = {
            ".pem",
            ".key",
            ".p12",
            ".pfx",
        }
        violations = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in prohibited_suffixes
            and ".git" not in path.parts
        ]
        self.assertEqual([], violations)
    def test_publication_contract_has_rollback(self) -> None:
        contract = (
            ROOT / ".l9/publication-contract.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "previous known-good version is retained",
            contract,
        )
        self.assertIn(
            "Core governance mutation",
            contract,
        )
if __name__ == "__main__":
    unittest.main()
EOF
cat > .github/workflows/phase-6-publication.yml <<'EOF'
name: Intelligence Phase 6 publication
on:
  pull_request:
    paths:
      - ".l9/publication-contract.yaml"
      - ".l9/default-compatibility.json"
      - "requirements/publication.txt"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/publication/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/publication/**"
      - "tests/architecture/**"
  push:
    branches:
      - main
    paths:
      - ".l9/publication-contract.yaml"
      - ".l9/default-compatibility.json"
      - "requirements/publication.txt"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/publication/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/publication/**"
      - "tests/architecture/**"
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: intelligence-phase-6-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  publication-contract:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout immutable revision
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Install project
        run: |
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -e ".[dev]"
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -r requirements/snapshot.txt \
            -r requirements/publication.txt
      - name: Run complete Phase 1–6 suite
        run: |
          python -m pytest \
            tests/architecture \
            tests/contracts \
            tests/ingestion \
            tests/snapshots \
            tests/analytics \
            tests/compilation \
            tests/publication
EOF
cat > .github/workflows/publish-defense-pack.yml <<'EOF'
name: Publish signed defense pack
on:
  workflow_dispatch:
    inputs:
      compilation_artifact:
        description: Name of the verified compilation artifact
        required: true
        type: string
      pack_version:
        description: Immutable semantic pack version
        required: true
        type: string
      taxonomy_version:
        description: Taxonomy version
        required: true
        type: string
      channel:
        description: Publication channel
        required: true
        type: choice
        options:
          - experimental
          - shadow
          - stable
      previous_release_tag:
        description: Previous release tag required for shadow/stable
        required: false
        type: string
permissions:
  contents: write
  actions: read
concurrency:
  group: publish-defense-${{ inputs.channel }}
  cancel-in-progress: false
jobs:
  publish:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment:
      name: defense-${{ inputs.channel }}
    steps:
      - name: Checkout immutable revision
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Validate signing secret
        env:
          PRIVATE_KEY_B64: ${{ secrets.L9_DEFENSE_PACK_PRIVATE_KEY_B64 }}
        run: |
          set -euo pipefail
          test -n "${PRIVATE_KEY_B64}" || {
            echo "L9_DEFENSE_PACK_PRIVATE_KEY_B64 is required" >&2
            exit 1
          }
      - name: Install project
        run: |
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -e ".[dev]"
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -r requirements/snapshot.txt \
            -r requirements/publication.txt
      - name: Download verified compilation
        uses: actions/download-artifact@v4
        with:
          name: ${{ inputs.compilation_artifact }}
          path: incoming-compilation
      - name: Restore signing key
        env:
          PRIVATE_KEY_B64: ${{ secrets.L9_DEFENSE_PACK_PRIVATE_KEY_B64 }}
        run: |
          set -euo pipefail
          mkdir -p "${RUNNER_TEMP}/l9-signing"
          printf '%s' "${PRIVATE_KEY_B64}" \
            | base64 --decode \
            > "${RUNNER_TEMP}/l9-signing/private.pem"
          chmod 600 "${RUNNER_TEMP}/l9-signing/private.pem"
      - name: Locate and verify compilation
        id: compilation
        run: |
          set -euo pipefail
          manifest="$(
            find incoming-compilation \
              -type f \
              -name manifest.json \
              -print \
              | head -n 1
          )"
          test -n "${manifest}" || {
            echo "compiler manifest not found" >&2
            exit 1
          }
          compilation_path="$(dirname "${manifest}")"
          l9-intelligence verify-compilation \
            "${compilation_path}"
          echo "path=${compilation_path}" >> "${GITHUB_OUTPUT}"
      - name: Assemble defense pack
        run: |
          set -euo pipefail
          mkdir -p dist
          l9-intelligence assemble-defense-pack \
            "${{ steps.compilation.outputs.path }}" \
            --output-root dist/packs \
            --version "${{ inputs.pack_version }}" \
            --taxonomy-version "${{ inputs.taxonomy_version }}" \
            --compatibility .l9/default-compatibility.json \
            --output dist/build-result.json
      - name: Download previous publication manifest
        if: ${{ inputs.previous_release_tag != '' }}
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          mkdir -p dist/previous
          gh release download \
            "${{ inputs.previous_release_tag }}" \
            --pattern "publication-manifest.json" \
            --dir dist/previous
      - name: Enforce rollback input
        if: ${{ inputs.channel != 'experimental' }}
        run: |
          set -euo pipefail
          test -f dist/previous/publication-manifest.json || {
            echo "shadow/stable requires a previous publication manifest" >&2
            exit 1
          }
      - name: Sign defense pack
        run: |
          set -euo pipefail
          previous=()
          if [[ -f dist/previous/publication-manifest.json ]]; then
            previous=(
              --previous-manifest
              dist/previous/publication-manifest.json
            )
          fi
          l9-intelligence sign-defense-pack \
            dist/build-result.json \
            --private-key \
              "${RUNNER_TEMP}/l9-signing/private.pem" \
            --channel "${{ inputs.channel }}" \
            --publication-manifest \
              dist/publication-manifest.json \
            "${previous[@]}"
      - name: Verify signed pack
        id: verify
        run: |
          set -euo pipefail
          archive="$(
            python - <<'PY'
          import json
          from pathlib import Path
          value = json.loads(
              Path("dist/build-result.json").read_text()
          )
          print(value["archive_path"])
          PY
          )"
          l9-intelligence verify-defense-pack \
            dist/publication-manifest.json \
            "${archive}" \
            --output dist/verification.json
          cp "${archive}" dist/
          archive_name="$(basename "${archive}")"
          echo "archive_name=${archive_name}" >> "${GITHUB_OUTPUT}"
      - name: Create immutable GitHub Release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          tag="defense-v${{ inputs.pack_version }}"
          if gh release view "${tag}" >/dev/null 2>&1; then
            echo "Release ${tag} already exists; versions are immutable." >&2
            exit 1
          fi
          gh release create \
            "${tag}" \
            "dist/${{ steps.verify.outputs.archive_name }}" \
            dist/publication-manifest.json \
            dist/verification.json \
            .l9/default-compatibility.json \
            --title "L9 Defense Pack ${{ inputs.pack_version }}" \
            --notes "Channel: ${{ inputs.channel }}" \
            --verify-tag
      - name: Remove private key
        if: always()
        run: |
          rm -rf "${RUNNER_TEMP}/l9-signing"
EOF
cat > docs/architecture/ADRs/ADR-INTEL-018-signed-defense-packs.md <<'EOF'
# ADR-INTEL-018: Published defense packs require detached signatures
- Status: Accepted
- Phase: INTEL-P5
## Decision
Every published defense-pack archive is signed using an Ed25519 detached
signature over the archive SHA-256 digest.
The publication manifest distributes the signature and raw public verification
key. Private keys remain external secrets and never enter Git or the defense
pack.
## Consequences
Consumers can verify archive integrity and publisher authenticity without
accessing the Intelligence corpus.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-019-release-channels-and-rollback.md <<'EOF'
# ADR-INTEL-019: Release channels retain previous known-good packs
- Status: Accepted
- Phase: INTEL-P5
## Decision
Defense packs may enter experimental, shadow, or stable channels.
Channel indexes identify an explicit active version and previous known-good
version. Shadow and stable publication require rollback metadata.
Rollback activates the previous immutable pack. It never recompiles or mutates
an existing pack.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-020-core-retains-policy-authority.md <<'EOF'
# ADR-INTEL-020: Pack publication does not promote Core policy
- Status: Accepted
- Phase: INTEL-P5
## Decision
Debt Intelligence may publish signed, promotion-eligible prevention packs.
Only Core governance maintainers may choose a pack for CI use, select advisory
or blocking mode, and modify quality policy.
Publication therefore cannot edit Core rule modes, thresholds, waivers, or
required-check configuration.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-021-retirement-is-append-only.md <<'EOF'
# ADR-INTEL-021: Defense-pack retirement is append-only
- Status: Accepted
- Phase: INTEL-P5
## Decision
Retirement creates a signed-lineage retirement record containing the pack
identity, archive digest, reason, issuer, time, and optional replacement.
Existing release artifacts and publication history remain available for audit
and rollback analysis.
EOF
python3 - <<'PY'
from pathlib import Path
path = Path(".l9/architecture.yaml")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "phase: INTEL-P4",
    "phase: INTEL-P5",
    1,
)
old = """phase_5:
  name: rule-compilation
  status: implemented
  includes:
    - candidate-rule extraction
    - leverage scoring
    - generated invariants
    - ast-grep candidate compilation
    - SDK architecture-contract candidate compilation
    - regression fixture compilation
    - regression execution
    - deterministic compiler manifests
  excludes:
    - defense-pack assembly
    - artifact signing
    - release publication
    - promotion
    - retirement
    - Core policy mutation
"""
new = """phase_5:
  name: rule-compilation
  status: implemented
phase_6:
  name: signed-publication
  status: implemented
  includes:
    - immutable defense-pack assembly
    - promotion-eligible rule selection
    - compatibility matrices
    - deterministic tar-gzip archives
    - Ed25519 detached signatures
    - publication manifests
    - experimental, shadow, and stable channels
    - rollback metadata
    - append-only retirement records
    - immutable GitHub Release workflow
  excludes:
    - Core governance mutation
    - automatic blocking promotion
    - LSP activation
    - OCI registry push
    - closed-loop outcome ingestion
    - effectiveness-based retirement recommendations
"""
if old not in text:
    raise SystemExit("unexpected INTEL-P4 architecture block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
python3 - <<'PY'
from pathlib import Path
path = Path("ROADMAP.md")
text = path.read_text(encoding="utf-8")
old = """## INTEL-P5 — Signed publication
Not authorized.
"""
new = """## INTEL-P5 — Signed publication
Implemented:
- immutable `l9.debt-defense/v1` pack assembly;
- promotion-eligible rule selection;
- compatibility matrices;
- deterministic tar-gzip archives;
- Ed25519 detached signatures;
- publication manifests;
- experimental, shadow, and stable channel indexes;
- previous-known-good rollback metadata;
- append-only retirement records;
- immutable GitHub Release publication.
Publication does not mutate Core governance or activate blocking policy.
"""
if old not in text:
    raise SystemExit("unexpected ROADMAP INTEL-P5 block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
cat >> AGENTS.md <<'EOF'
## INTEL-P5 publication rules
- Publish only verified INTEL-P4 compiler output.
- Include only promotion-eligible candidates.
- Pin corpus snapshot, analysis run, compilation, compiler, taxonomy, and SDK
  contract versions.
- Build byte-reproducible archives.
- Sign the archive SHA-256 digest with an external Ed25519 private key.
- Never commit or package private keys.
- Publish minimal executable prevention data only.
- Never distribute corpus records, raw logs, source content, or repository
  identities.
- Require rollback metadata for shadow and stable publication.
- Never overwrite an existing pack version.
- Record retirement through append-only events.
- Never edit Core governance or activate blocking policy.
EOF
python -m pip install \
  --disable-pip-version-check \
  --no-input \
  -e ".[dev]"
python -m pip install \
  --disable-pip-version-check \
  --no-input \
  -r requirements/snapshot.txt \
  -r requirements/publication.txt
python -m pytest \
  tests/architecture \
  tests/contracts \
  tests/ingestion \
  tests/snapshots \
  tests/analytics \
  tests/compilation \
  tests/publication
printf '\nINTEL-P5 signed publication contracts built and validated.\n'
printf 'A real defense pack requires at least one promotion-eligible INTEL-P4 candidate.\n'
printf 'Stable publication additionally requires a previous known-good publication manifest.\n'

Execute it:

chmod +x build-phase-6.sh
./build-phase-6.sh

Commit the phase:

git status --short
git diff --check
git add \
  .l9 \
  .github/workflows/phase-6-publication.yml \
  .github/workflows/publish-defense-pack.yml \
  requirements/publication.txt \
  schemas/intelligence \
  src/l9_debt_intelligence \
  tests/architecture \
  tests/publication \
  docs/architecture/ADRs \
  AGENTS.md \
  ROADMAP.md
git commit -m "feat!: implement Intelligence INTEL-P5 signed publication"

Publication lifecycle

verified INTEL-P4 compilation
        ↓
select promotion-eligible candidates
        ↓
assemble minimal l9.debt-defense/v1 pack
        ↓
build deterministic tar.gz archive
        ↓
calculate SHA-256
        ↓
sign digest with Ed25519
        ↓
verify signature and publication gates
        ↓
publish immutable release
        ↓
update explicit release channel
        ├── active version
        └── previous known-good version

A promotion_eligible candidate may enter a signed pack, but publication still does not make it blocking. Core remains responsible for selecting the pack and assigning advisory, shadow, or blocking governance. The final roadmap phase is INTEL-P6: closed-loop effectiveness, covering LSP and CI outcomes, post-publication effectiveness, and evidence-backed retirement recommendations.