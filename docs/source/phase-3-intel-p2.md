The next phase is INTEL-P2: immutable corpus snapshots.

The current repository still exposes the legacy offense/defense pipeline and generated working-tree outputs, while the converged architecture requires corpus snapshots, Parquet partitions, DuckDB-based local analytics, and immutable publication manifests.  The uploaded repository specification assigns this phase immutable corpus snapshots, Parquet storage, DuckDB analytics, and snapshot manifests while keeping recurrence analysis and rule compilation in later phases. repo-spec.yaml

Save this as build-phase-3.sh in the INTEL-P1 repository.

#!/usr/bin/env bash
set -euo pipefail
require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    printf 'INTEL-P2 requires INTEL-P1 file: %s\n' "$path" >&2
    exit 1
  fi
}
require_file ".l9/architecture.yaml"
require_file ".l9/ingestion-contract.yaml"
require_file "schemas/intelligence/corpus-record.schema.json"
require_file "src/l9_debt_intelligence/ingestion/storage.py"
require_file "src/l9_debt_intelligence/ingestion/verify.py"
mkdir -p \
  .github/workflows \
  docs/architecture/ADRs \
  requirements \
  schemas/intelligence \
  src/l9_debt_intelligence/snapshots \
  tests/snapshots \
  tests/fixtures/snapshots
cat > requirements/snapshot.txt <<'EOF'
duckdb>=1.1,<2
pyarrow>=17,<20
EOF
cat > .l9/snapshot-contract.yaml <<'EOF'
schema: l9.intelligence-snapshot-contract/v1
metadata:
  repository: Quantum-L9/l9-ci-debt-intelligence
  phase: INTEL-P2
  status: authoritative
purpose: >
  Materialize immutable, reproducible corpus snapshots from verified INTEL-P1
  accepted records without rewriting ingestion history.
source:
  accepted_records: var/intelligence/records
  ingestion_ledger: var/intelligence/ledger/events.jsonl
  required_verification: l9.ingestion-verification/v1
snapshot_identity:
  algorithm: SHA-256
  prefix: cs_
  inputs:
    - schema_version
    - ordered_record_ids
    - ordered_record_hashes
    - partition_plan
    - snapshot_format_version
    - SDK_contract_version
  excluded:
    - build_time
    - filesystem_paths
    - machine_identity
    - process_identity
    - record_arrival_order
storage:
  format: Parquet
  compression: zstd
  logical_partitioning:
    - event_class
    - producer_id
  row_order:
    - record_id
  timestamps:
    representation: UTC
  prohibited:
    - mutable latest directory as authority
    - unversioned snapshot replacement
    - embedding source content
    - embedding secret values
    - embedding absolute paths
manifest:
  required:
    - snapshot_id
    - format_version
    - SDK_contract_version
    - record_count
    - partition_count
    - ordered_partition_hashes
    - source_record_set_hash
    - deterministic_output_hash
    - build_metadata
    - limitations
  build_metadata:
    informational_only:
      - created_at
      - implementation_version
      - pyarrow_version
      - duckdb_version
duckdb:
  role: local analytical projection
  authority: derived
  persistence: optional
  requirements:
    - read snapshot Parquet partitions
    - expose deterministic corpus_records view
    - never mutate source Parquet
    - never become corpus authority
immutability:
  rules:
    - existing snapshot objects are never overwritten
    - identical inputs resolve to the same snapshot identity
    - identical inputs produce byte-identical logical manifests
    - hash mismatch terminates publication
    - snapshot correction requires a new snapshot
phase_3:
  includes:
    - deterministic snapshot planning
    - immutable Parquet partition generation
    - snapshot manifest generation
    - source record set hashing
    - partition hashing
    - snapshot verification
    - DuckDB read-only analytical projection
    - snapshot CLI
  excludes:
    - recurrence metrics
    - co-occurrence metrics
    - effort modelling
    - rule effectiveness
    - candidate rules
    - defense-pack compilation
    - signing
    - release publication
EOF
cat > schemas/intelligence/corpus-snapshot.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/corpus-snapshot/v1",
  "title": "L9 Intelligence Corpus Snapshot",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "snapshot_id",
    "format_version",
    "sdk_contract_version",
    "record_count",
    "partition_count",
    "source_record_set_hash",
    "deterministic_output_hash",
    "partitions",
    "build_metadata",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.corpus-snapshot/v1"
    },
    "snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "format_version": {
      "const": "l9.corpus-snapshot-format/v1"
    },
    "sdk_contract_version": {
      "type": "string",
      "minLength": 1
    },
    "record_count": {
      "type": "integer",
      "minimum": 0
    },
    "partition_count": {
      "type": "integer",
      "minimum": 0
    },
    "source_record_set_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "deterministic_output_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "partitions": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/partition"
      }
    },
    "build_metadata": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "created_at",
        "implementation_version",
        "pyarrow_version",
        "duckdb_version"
      ],
      "properties": {
        "created_at": {
          "type": "string",
          "format": "date-time"
        },
        "implementation_version": {
          "type": "string"
        },
        "pyarrow_version": {
          "type": "string"
        },
        "duckdb_version": {
          "type": "string"
        }
      }
    },
    "limitations": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "uniqueItems": true
    }
  },
  "$defs": {
    "partition": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "event_class",
        "producer_id",
        "relative_path",
        "record_count",
        "sha256"
      ],
      "properties": {
        "event_class": {
          "type": "string",
          "minLength": 1
        },
        "producer_id": {
          "type": "string",
          "minLength": 1
        },
        "relative_path": {
          "type": "string",
          "pattern": "^partitions/"
        },
        "record_count": {
          "type": "integer",
          "minimum": 1
        },
        "sha256": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$"
        }
      }
    }
  }
}
EOF
cat > schemas/intelligence/snapshot-verification.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/snapshot-verification/v1",
  "title": "L9 Intelligence Snapshot Verification",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "status",
    "snapshot_id",
    "record_count",
    "partition_count",
    "verified_partition_count",
    "deterministic_output_hash"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.snapshot-verification/v1"
    },
    "status": {
      "const": "valid"
    },
    "snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "record_count": {
      "type": "integer",
      "minimum": 0
    },
    "partition_count": {
      "type": "integer",
      "minimum": 0
    },
    "verified_partition_count": {
      "type": "integer",
      "minimum": 0
    },
    "deterministic_output_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    }
  }
}
EOF
cat > src/l9_debt_intelligence/snapshots/__init__.py <<'EOF'
"""Immutable corpus snapshot construction and verification."""
EOF
cat > src/l9_debt_intelligence/snapshots/errors.py <<'EOF'
from __future__ import annotations
class SnapshotError(RuntimeError):
    """Base error for immutable corpus snapshots."""
class SnapshotSourceError(SnapshotError):
    """The ingestion source is missing or invalid."""
class SnapshotCollisionError(SnapshotError):
    """An immutable snapshot path already contains different content."""
class SnapshotVerificationError(SnapshotError):
    """A snapshot failed integrity or semantic verification."""
EOF
cat > src/l9_debt_intelligence/snapshots/models.py <<'EOF'
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
@dataclass(frozen=True)
class SnapshotRecord:
    record_id: str
    source_event_id: str
    producer_id: str
    event_class: str
    lifecycle_state: str
    redaction_status: str
    producer_contract: str
    payload_content_hash: str
    limitations_json: str
    superseded_by: str | None
    source_record_hash: str
@dataclass(frozen=True)
class PartitionPlan:
    event_class: str
    producer_id: str
    relative_path: Path
    records: tuple[SnapshotRecord, ...]
@dataclass(frozen=True)
class SnapshotBuildResult:
    snapshot_id: str
    snapshot_path: Path
    manifest_path: Path
    record_count: int
    partition_count: int
    deterministic_output_hash: str
    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "l9.snapshot-build-result/v1",
            "snapshot_id": self.snapshot_id,
            "snapshot_path": self.snapshot_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "record_count": self.record_count,
            "partition_count": self.partition_count,
            "deterministic_output_hash": (
                self.deterministic_output_hash
            ),
        }
EOF
cat > src/l9_debt_intelligence/snapshots/hashing.py <<'EOF'
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()
def namespaced_document_hash(prefix: str, value: Any) -> str:
    return prefix + sha256_bytes(canonical_json(value))
EOF
cat > src/l9_debt_intelligence/snapshots/source.py <<'EOF'
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import sha256_document
from l9_debt_intelligence.ingestion.verify import verify_store
from .errors import SnapshotSourceError
from .models import SnapshotRecord
def load_verified_records(storage_root: Path) -> tuple[SnapshotRecord, ...]:
    verification = verify_store(storage_root)
    if verification.get("status") != "valid":
        raise SnapshotSourceError(
            "ingestion store verification did not return valid"
        )
    records_root = storage_root / "records"
    records: list[SnapshotRecord] = []
    for path in sorted(records_root.glob("cr_*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise SnapshotSourceError(
                f"record is not an object: {path}"
            )
        payload_reference = document.get("payload_reference")
        if not isinstance(payload_reference, dict):
            raise SnapshotSourceError(
                f"record has no payload_reference: {path}"
            )
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
            raise SnapshotSourceError(
                f"record limitations must be a list: {path}"
            )
        records.append(
            SnapshotRecord(
                record_id=str(record_id),
                source_event_id=str(document["source_event_id"]),
                producer_id=str(document["producer_id"]),
                event_class=str(document["event_class"]),
                lifecycle_state=str(lifecycle_state),
                redaction_status=str(document["redaction_status"]),
                producer_contract=str(
                    payload_reference["producer_contract"]
                ),
                payload_content_hash=str(
                    payload_reference["content_hash"]
                ),
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
EOF
cat > src/l9_debt_intelligence/snapshots/planner.py <<'EOF'
from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
from .models import PartitionPlan, SnapshotRecord
SAFE_COMPONENT = re.compile(r"[^A-Za-z0-9._-]+")
def safe_component(value: str) -> str:
    normalized = SAFE_COMPONENT.sub("_", value).strip("._")
    if not normalized:
        return "unknown"
    return normalized[:120]
def plan_partitions(
    records: tuple[SnapshotRecord, ...],
) -> tuple[PartitionPlan, ...]:
    groups: dict[
        tuple[str, str],
        list[SnapshotRecord],
    ] = defaultdict(list)
    for record in records:
        groups[(record.event_class, record.producer_id)].append(record)
    plans: list[PartitionPlan] = []
    for event_class, producer_id in sorted(groups):
        partition_records = tuple(
            sorted(
                groups[(event_class, producer_id)],
                key=lambda value: value.record_id,
            )
        )
        relative_path = (
            Path("partitions")
            / f"event_class={safe_component(event_class)}"
            / f"producer_id={safe_component(producer_id)}"
            / "records.parquet"
        )
        plans.append(
            PartitionPlan(
                event_class=event_class,
                producer_id=producer_id,
                relative_path=relative_path,
                records=partition_records,
            )
        )
    return tuple(plans)
EOF
cat > src/l9_debt_intelligence/snapshots/parquet.py <<'EOF'
from __future__ import annotations
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from .models import PartitionPlan
SCHEMA = pa.schema(
    [
        pa.field("record_id", pa.string(), nullable=False),
        pa.field("source_event_id", pa.string(), nullable=False),
        pa.field("producer_id", pa.string(), nullable=False),
        pa.field("event_class", pa.string(), nullable=False),
        pa.field("lifecycle_state", pa.string(), nullable=False),
        pa.field("redaction_status", pa.string(), nullable=False),
        pa.field("producer_contract", pa.string(), nullable=False),
        pa.field("payload_content_hash", pa.string(), nullable=False),
        pa.field("limitations_json", pa.string(), nullable=False),
        pa.field("superseded_by", pa.string(), nullable=True),
        pa.field("source_record_hash", pa.string(), nullable=False),
    ]
)
def write_partition(
    destination: Path,
    plan: PartitionPlan,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    columns = {
        "record_id": [],
        "source_event_id": [],
        "producer_id": [],
        "event_class": [],
        "lifecycle_state": [],
        "redaction_status": [],
        "producer_contract": [],
        "payload_content_hash": [],
        "limitations_json": [],
        "superseded_by": [],
        "source_record_hash": [],
    }
    for record in plan.records:
        columns["record_id"].append(record.record_id)
        columns["source_event_id"].append(record.source_event_id)
        columns["producer_id"].append(record.producer_id)
        columns["event_class"].append(record.event_class)
        columns["lifecycle_state"].append(record.lifecycle_state)
        columns["redaction_status"].append(record.redaction_status)
        columns["producer_contract"].append(
            record.producer_contract
        )
        columns["payload_content_hash"].append(
            record.payload_content_hash
        )
        columns["limitations_json"].append(
            record.limitations_json
        )
        columns["superseded_by"].append(record.superseded_by)
        columns["source_record_hash"].append(
            record.source_record_hash
        )
    table = pa.Table.from_pydict(columns, schema=SCHEMA)
    pq.write_table(
        table,
        destination,
        compression="zstd",
        use_dictionary=False,
        write_statistics=True,
        data_page_version="1.0",
        version="2.6",
        row_group_size=max(1, len(plan.records)),
        store_schema=True,
    )
EOF
cat > src/l9_debt_intelligence/snapshots/builder.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable
import duckdb
import pyarrow
from l9_debt_intelligence import __version__
from l9_debt_intelligence.contracts.canonical import canonical_json
from .errors import SnapshotCollisionError, SnapshotError
from .hashing import (
    namespaced_document_hash,
    sha256_bytes,
    sha256_file,
)
from .models import SnapshotBuildResult
from .parquet import write_partition
from .planner import plan_partitions
from .source import load_verified_records
Clock = Callable[[], dt.datetime]
FORMAT_VERSION = "l9.corpus-snapshot-format/v1"
SDK_CONTRACT_VERSION = "l9.integration-contract/v1"
def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)
def format_time(value: dt.datetime) -> str:
    if value.tzinfo is None:
        raise SnapshotError(
            "snapshot clock must return a timezone-aware value"
        )
    return value.astimezone(dt.timezone.utc).isoformat().replace(
        "+00:00",
        "Z",
    )
def build_snapshot(
    *,
    storage_root: Path,
    snapshots_root: Path,
    clock: Clock = utc_now,
) -> SnapshotBuildResult:
    records = load_verified_records(storage_root)
    plans = plan_partitions(records)
    source_set = [
        {
            "record_id": record.record_id,
            "source_record_hash": record.source_record_hash,
        }
        for record in records
    ]
    source_record_set_hash = sha256_bytes(
        canonical_json(source_set)
    )
    identity_document = {
        "format_version": FORMAT_VERSION,
        "sdk_contract_version": SDK_CONTRACT_VERSION,
        "records": source_set,
        "partition_plan": [
            {
                "event_class": plan.event_class,
                "producer_id": plan.producer_id,
                "relative_path": plan.relative_path.as_posix(),
                "record_ids": [
                    record.record_id for record in plan.records
                ],
            }
            for plan in plans
        ],
    }
    snapshot_id = namespaced_document_hash(
        "cs_",
        identity_document,
    )
    destination = snapshots_root.resolve() / snapshot_id
    temporary_parent = snapshots_root.resolve()
    temporary_parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{snapshot_id}.",
            dir=temporary_parent,
        )
    )
    try:
        partition_entries: list[dict[str, object]] = []
        for plan in plans:
            partition_path = temporary / plan.relative_path
            write_partition(partition_path, plan)
            partition_entries.append(
                {
                    "event_class": plan.event_class,
                    "producer_id": plan.producer_id,
                    "relative_path": plan.relative_path.as_posix(),
                    "record_count": len(plan.records),
                    "sha256": sha256_file(partition_path),
                }
            )
        deterministic_document = {
            "snapshot_id": snapshot_id,
            "format_version": FORMAT_VERSION,
            "sdk_contract_version": SDK_CONTRACT_VERSION,
            "record_count": len(records),
            "partition_count": len(partition_entries),
            "source_record_set_hash": source_record_set_hash,
            "partitions": partition_entries,
            "limitations": [],
        }
        deterministic_output_hash = sha256_bytes(
            canonical_json(deterministic_document)
        )
        manifest = {
            "schema_version": "l9.corpus-snapshot/v1",
            **deterministic_document,
            "deterministic_output_hash": deterministic_output_hash,
            "build_metadata": {
                "created_at": format_time(clock()),
                "implementation_version": __version__,
                "pyarrow_version": pyarrow.__version__,
                "duckdb_version": duckdb.__version__,
            },
        }
        manifest_path = temporary / "manifest.json"
        manifest_path.write_bytes(
            canonical_json(manifest) + b"\n"
        )
        if destination.exists():
            existing_manifest = destination / "manifest.json"
            if not existing_manifest.is_file():
                raise SnapshotCollisionError(
                    f"existing snapshot has no manifest: {destination}"
                )
            existing = json.loads(
                existing_manifest.read_text(encoding="utf-8")
            )
            if (
                existing.get("deterministic_output_hash")
                != deterministic_output_hash
            ):
                raise SnapshotCollisionError(
                    f"snapshot identity collision: {snapshot_id}"
                )
            shutil.rmtree(temporary)
        else:
            os.replace(temporary, destination)
        return SnapshotBuildResult(
            snapshot_id=snapshot_id,
            snapshot_path=destination,
            manifest_path=destination / "manifest.json",
            record_count=len(records),
            partition_count=len(partition_entries),
            deterministic_output_hash=deterministic_output_hash,
        )
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
EOF
cat > src/l9_debt_intelligence/snapshots/verify.py <<'EOF'
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pyarrow.parquet as pq
from l9_debt_intelligence.contracts.canonical import canonical_json
from .errors import SnapshotVerificationError
from .hashing import sha256_bytes, sha256_file
def verify_snapshot(snapshot_path: Path) -> dict[str, Any]:
    snapshot_path = snapshot_path.resolve()
    manifest_path = snapshot_path / "manifest.json"
    if not manifest_path.is_file():
        raise SnapshotVerificationError(
            f"snapshot manifest does not exist: {manifest_path}"
        )
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    if manifest.get("schema_version") != "l9.corpus-snapshot/v1":
        raise SnapshotVerificationError(
            "unsupported snapshot manifest schema"
        )
    if manifest.get("snapshot_id") != snapshot_path.name:
        raise SnapshotVerificationError(
            "snapshot directory does not match snapshot identity"
        )
    partitions = manifest.get("partitions")
    if not isinstance(partitions, list):
        raise SnapshotVerificationError(
            "snapshot partitions must be a list"
        )
    total_rows = 0
    for partition in partitions:
        if not isinstance(partition, dict):
            raise SnapshotVerificationError(
                "snapshot partition entry must be an object"
            )
        relative_path = partition.get("relative_path")
        if not isinstance(relative_path, str):
            raise SnapshotVerificationError(
                "partition relative_path must be a string"
            )
        path = (snapshot_path / relative_path).resolve()
        try:
            path.relative_to(snapshot_path)
        except ValueError as error:
            raise SnapshotVerificationError(
                "partition path escapes snapshot root"
            ) from error
        if not path.is_file():
            raise SnapshotVerificationError(
                f"partition does not exist: {relative_path}"
            )
        actual_hash = sha256_file(path)
        if actual_hash != partition.get("sha256"):
            raise SnapshotVerificationError(
                f"partition hash mismatch: {relative_path}"
            )
        table = pq.read_table(path)
        row_count = table.num_rows
        if row_count != partition.get("record_count"):
            raise SnapshotVerificationError(
                f"partition row count mismatch: {relative_path}"
            )
        record_ids = table.column("record_id").to_pylist()
        if record_ids != sorted(record_ids):
            raise SnapshotVerificationError(
                f"partition row order is not deterministic: {relative_path}"
            )
        total_rows += row_count
    if total_rows != manifest.get("record_count"):
        raise SnapshotVerificationError(
            "manifest record count does not match partitions"
        )
    deterministic_document = {
        "snapshot_id": manifest["snapshot_id"],
        "format_version": manifest["format_version"],
        "sdk_contract_version": manifest[
            "sdk_contract_version"
        ],
        "record_count": manifest["record_count"],
        "partition_count": manifest["partition_count"],
        "source_record_set_hash": manifest[
            "source_record_set_hash"
        ],
        "partitions": manifest["partitions"],
        "limitations": manifest["limitations"],
    }
    actual_output_hash = sha256_bytes(
        canonical_json(deterministic_document)
    )
    if (
        actual_output_hash
        != manifest.get("deterministic_output_hash")
    ):
        raise SnapshotVerificationError(
            "deterministic output hash mismatch"
        )
    return {
        "schema_version": "l9.snapshot-verification/v1",
        "status": "valid",
        "snapshot_id": manifest["snapshot_id"],
        "record_count": total_rows,
        "partition_count": len(partitions),
        "verified_partition_count": len(partitions),
        "deterministic_output_hash": actual_output_hash,
    }
EOF
cat > src/l9_debt_intelligence/snapshots/duckdb_projection.py <<'EOF'
from __future__ import annotations
from pathlib import Path
import duckdb
from .verify import verify_snapshot
def create_projection(
    *,
    snapshot_path: Path,
    database_path: Path,
) -> Path:
    verification = verify_snapshot(snapshot_path)
    if verification["status"] != "valid":
        raise RuntimeError("snapshot verification failed")
    parquet_glob = (
        snapshot_path.resolve()
        / "partitions"
        / "**"
        / "*.parquet"
    )
    database_path = database_path.resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(database_path))
    try:
        connection.execute(
            """
            CREATE OR REPLACE VIEW corpus_records AS
            SELECT *
            FROM read_parquet(?, union_by_name = true)
            ORDER BY record_id
            """,
            [parquet_glob.as_posix()],
        )
        connection.execute(
            """
            CREATE OR REPLACE TABLE snapshot_metadata AS
            SELECT
                ?::VARCHAR AS snapshot_id,
                ?::BIGINT AS record_count,
                ?::BIGINT AS partition_count
            """,
            [
                verification["snapshot_id"],
                verification["record_count"],
                verification["partition_count"],
            ],
        )
        connection.execute("CHECKPOINT")
    finally:
        connection.close()
    return database_path
EOF
python3 - <<'PY'
from pathlib import Path
path = Path("src/l9_debt_intelligence/cli.py")
text = path.read_text(encoding="utf-8")
import_anchor = (
    "from .ingestion.verify import verify_store\n"
)
replacement = """from .ingestion.verify import verify_store
from .snapshots.builder import build_snapshot
from .snapshots.duckdb_projection import create_projection
from .snapshots.verify import verify_snapshot
"""
if replacement not in text:
    if import_anchor not in text:
        raise SystemExit("unexpected CLI imports")
    text = text.replace(import_anchor, replacement)
parser_anchor = """    verify.add_argument("--output", type=Path)
    return parser
"""
parser_replacement = """    verify.add_argument("--output", type=Path)
    snapshot = commands.add_parser(
        "build-snapshot",
        help="Build an immutable corpus snapshot.",
    )
    snapshot.add_argument(
        "--storage-root",
        type=Path,
        required=True,
    )
    snapshot.add_argument(
        "--snapshots-root",
        type=Path,
        required=True,
    )
    snapshot.add_argument("--output", type=Path)
    verify_snapshot_parser = commands.add_parser(
        "verify-snapshot",
        help="Verify an immutable corpus snapshot.",
    )
    verify_snapshot_parser.add_argument(
        "snapshot",
        type=Path,
    )
    verify_snapshot_parser.add_argument("--output", type=Path)
    projection = commands.add_parser(
        "create-duckdb-projection",
        help="Create a derived DuckDB projection.",
    )
    projection.add_argument(
        "snapshot",
        type=Path,
    )
    projection.add_argument(
        "--database",
        type=Path,
        required=True,
    )
    projection.add_argument("--output", type=Path)
    return parser
"""
if parser_replacement not in text:
    if parser_anchor not in text:
        raise SystemExit("unexpected CLI parser")
    text = text.replace(parser_anchor, parser_replacement)
command_anchor = """        elif arguments.command == "verify-store":
            document = verify_store(arguments.storage_root)
            exit_code = 0
        else:
            return 2
"""
command_replacement = """        elif arguments.command == "verify-store":
            document = verify_store(arguments.storage_root)
            exit_code = 0
        elif arguments.command == "build-snapshot":
            result = build_snapshot(
                storage_root=arguments.storage_root,
                snapshots_root=arguments.snapshots_root,
            )
            document = result.as_dict()
            exit_code = 0
        elif arguments.command == "verify-snapshot":
            document = verify_snapshot(arguments.snapshot)
            exit_code = 0
        elif arguments.command == "create-duckdb-projection":
            database = create_projection(
                snapshot_path=arguments.snapshot,
                database_path=arguments.database,
            )
            document = {
                "schema_version": "l9.duckdb-projection-result/v1",
                "status": "created",
                "database": database.as_posix(),
            }
            exit_code = 0
        else:
            return 2
"""
if command_replacement not in text:
    if command_anchor not in text:
        raise SystemExit("unexpected CLI command dispatcher")
    text = text.replace(command_anchor, command_replacement)
path.write_text(text, encoding="utf-8")
PY
cat > tests/snapshots/test_snapshot_builder.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.ingestion.service import IngestionService
from l9_debt_intelligence.snapshots.builder import build_snapshot
from l9_debt_intelligence.snapshots.verify import verify_snapshot
ROOT = Path(__file__).resolve().parents[2]
def fixed_clock() -> dt.datetime:
    return dt.datetime(
        2026,
        7,
        17,
        12,
        0,
        tzinfo=dt.timezone.utc,
    )
class SnapshotBuilderTests(unittest.TestCase):
    def event(self) -> dict:
        return json.loads(
            (
                ROOT
                / "tests/fixtures/producers/valid-core-gate.json"
            ).read_text(encoding="utf-8")
        )
    def ingest(self, storage: Path) -> None:
        service = IngestionService(
            event_schema=(
                ROOT / "schemas/intelligence/corpus-event.schema.json"
            ),
            compatibility_registry=(
                ROOT / ".l9/producer-compatibility.json"
            ),
            storage_root=storage,
            clock=fixed_clock,
        )
        result = service.ingest(self.event())
        self.assertEqual("accepted", result.status)
    def test_snapshot_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storage = root / "ingestion"
            snapshots = root / "snapshots"
            self.ingest(storage)
            first = build_snapshot(
                storage_root=storage,
                snapshots_root=snapshots,
                clock=fixed_clock,
            )
            second = build_snapshot(
                storage_root=storage,
                snapshots_root=snapshots,
                clock=fixed_clock,
            )
            self.assertEqual(first.snapshot_id, second.snapshot_id)
            self.assertEqual(
                first.deterministic_output_hash,
                second.deterministic_output_hash,
            )
            self.assertEqual(1, first.record_count)
            self.assertEqual(1, first.partition_count)
    def test_snapshot_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storage = root / "ingestion"
            snapshots = root / "snapshots"
            self.ingest(storage)
            result = build_snapshot(
                storage_root=storage,
                snapshots_root=snapshots,
                clock=fixed_clock,
            )
            verification = verify_snapshot(result.snapshot_path)
            self.assertEqual("valid", verification["status"])
            self.assertEqual(result.snapshot_id, verification["snapshot_id"])
            self.assertEqual(1, verification["record_count"])
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/snapshots/test_snapshot_identity.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)
class SnapshotIdentityTests(unittest.TestCase):
    def test_mapping_order_does_not_change_identity(self) -> None:
        first = namespaced_document_hash(
            "cs_",
            {
                "b": 2,
                "a": 1,
            },
        )
        second = namespaced_document_hash(
            "cs_",
            {
                "a": 1,
                "b": 2,
            },
        )
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("cs_"))
        self.assertEqual(67, len(first))
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/snapshots/test_duckdb_projection.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
import duckdb
from l9_debt_intelligence.ingestion.service import IngestionService
from l9_debt_intelligence.snapshots.builder import build_snapshot
from l9_debt_intelligence.snapshots.duckdb_projection import (
    create_projection,
)
ROOT = Path(__file__).resolve().parents[2]
def fixed_clock() -> dt.datetime:
    return dt.datetime(
        2026,
        7,
        17,
        12,
        0,
        tzinfo=dt.timezone.utc,
    )
class DuckDBProjectionTests(unittest.TestCase):
    def test_projection_reads_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storage = root / "ingestion"
            snapshots = root / "snapshots"
            database = root / "analytics/corpus.duckdb"
            event = json.loads(
                (
                    ROOT
                    / "tests/fixtures/producers/valid-core-gate.json"
                ).read_text(encoding="utf-8")
            )
            service = IngestionService(
                event_schema=(
                    ROOT
                    / "schemas/intelligence/corpus-event.schema.json"
                ),
                compatibility_registry=(
                    ROOT / ".l9/producer-compatibility.json"
                ),
                storage_root=storage,
                clock=fixed_clock,
            )
            service.ingest(event)
            snapshot = build_snapshot(
                storage_root=storage,
                snapshots_root=snapshots,
                clock=fixed_clock,
            )
            create_projection(
                snapshot_path=snapshot.snapshot_path,
                database_path=database,
            )
            connection = duckdb.connect(
                str(database),
                read_only=True,
            )
            try:
                count = connection.execute(
                    "SELECT COUNT(*) FROM corpus_records"
                ).fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(1, count)
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/snapshots/test_snapshot_tampering.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.ingestion.service import IngestionService
from l9_debt_intelligence.snapshots.builder import build_snapshot
from l9_debt_intelligence.snapshots.errors import (
    SnapshotVerificationError,
)
from l9_debt_intelligence.snapshots.verify import verify_snapshot
ROOT = Path(__file__).resolve().parents[2]
def fixed_clock() -> dt.datetime:
    return dt.datetime(
        2026,
        7,
        17,
        12,
        0,
        tzinfo=dt.timezone.utc,
    )
class SnapshotTamperingTests(unittest.TestCase):
    def test_partition_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storage = root / "ingestion"
            snapshots = root / "snapshots"
            event = json.loads(
                (
                    ROOT
                    / "tests/fixtures/producers/valid-core-gate.json"
                ).read_text(encoding="utf-8")
            )
            service = IngestionService(
                event_schema=(
                    ROOT
                    / "schemas/intelligence/corpus-event.schema.json"
                ),
                compatibility_registry=(
                    ROOT / ".l9/producer-compatibility.json"
                ),
                storage_root=storage,
                clock=fixed_clock,
            )
            service.ingest(event)
            result = build_snapshot(
                storage_root=storage,
                snapshots_root=snapshots,
                clock=fixed_clock,
            )
            manifest = json.loads(
                result.manifest_path.read_text(encoding="utf-8")
            )
            partition = (
                result.snapshot_path
                / manifest["partitions"][0]["relative_path"]
            )
            with partition.open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaises(SnapshotVerificationError):
                verify_snapshot(result.snapshot_path)
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/architecture/test_snapshot_boundary.py <<'EOF'
from __future__ import annotations
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/snapshots"
class SnapshotBoundaryTests(unittest.TestCase):
    def test_snapshot_layer_contains_no_learning_or_compilation(self) -> None:
        prohibited = (
            "cooccurrence",
            "recurrence",
            "effort_atlas",
            "candidate_rule",
            "ast_grep",
            "defense_pack",
            "git push",
            "create_pull_request",
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for value in prohibited:
                if value in text:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{value}"
                    )
        self.assertEqual([], violations)
    def test_snapshot_contract_declares_immutability(self) -> None:
        contract = (
            ROOT / ".l9/snapshot-contract.yaml"
        ).read_text(encoding="utf-8")
        required = (
            "existing snapshot objects are never overwritten",
            "identical inputs resolve to the same snapshot identity",
            "DuckDB",
            "Parquet",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, contract)
if __name__ == "__main__":
    unittest.main()
EOF
cat > .github/workflows/phase-3-snapshots.yml <<'EOF'
name: Intelligence Phase 3 snapshots
on:
  pull_request:
    paths:
      - ".l9/snapshot-contract.yaml"
      - "requirements/snapshot.txt"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/snapshots/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/snapshots/**"
      - "tests/architecture/**"
  push:
    branches:
      - main
    paths:
      - ".l9/snapshot-contract.yaml"
      - "requirements/snapshot.txt"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/snapshots/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/snapshots/**"
      - "tests/architecture/**"
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: intelligence-phase-3-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  snapshots:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout immutable event revision
        env:
          REPOSITORY: ${{ github.repository }}
          REVISION: ${{ github.sha }}
          TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          git init .
          git remote add origin \
            "https://x-access-token:${TOKEN}@github.com/${REPOSITORY}.git"
          git -c protocol.version=2 fetch --depth=1 origin "${REVISION}"
          git checkout --detach FETCH_HEAD
          git remote set-url origin \
            "https://github.com/${REPOSITORY}.git"
      - name: Install project and snapshot dependencies
        run: |
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -e ".[dev]"
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -r requirements/snapshot.txt
      - name: Run architecture and snapshot tests
        run: |
          python -m pytest \
            tests/architecture \
            tests/contracts \
            tests/ingestion \
            tests/snapshots
      - name: Exercise snapshot lifecycle
        run: |
          set -euo pipefail
          workspace="$(mktemp -d)"
          ingestion="${workspace}/ingestion"
          snapshots="${workspace}/snapshots"
          database="${workspace}/analytics/corpus.duckdb"
          l9-intelligence ingest-event \
            tests/fixtures/producers/valid-core-gate.json \
            --storage-root "${ingestion}"
          l9-intelligence build-snapshot \
            --storage-root "${ingestion}" \
            --snapshots-root "${snapshots}" \
            --output "${workspace}/build.json"
          snapshot_id="$(
            python - "${workspace}/build.json" <<'PY'
          import json
          import sys
          from pathlib import Path
          value = json.loads(
              Path(sys.argv[1]).read_text(encoding="utf-8")
          )
          print(value["snapshot_id"])
          PY
          )"
          snapshot="${snapshots}/${snapshot_id}"
          l9-intelligence verify-snapshot \
            "${snapshot}" \
            --output "${workspace}/verification.json"
          l9-intelligence create-duckdb-projection \
            "${snapshot}" \
            --database "${database}" \
            --output "${workspace}/projection.json"
          python - "${workspace}/verification.json" <<'PY'
          import json
          import sys
          from pathlib import Path
          value = json.loads(
              Path(sys.argv[1]).read_text(encoding="utf-8")
          )
          assert value["status"] == "valid", value
          assert value["record_count"] == 1, value
          assert value["partition_count"] == 1, value
          PY
EOF
cat > docs/architecture/ADRs/ADR-INTEL-009-immutable-corpus-snapshots.md <<'EOF'
# ADR-INTEL-009: Corpus snapshots are immutable and content-addressed
- Status: Accepted
- Phase: INTEL-P2
## Decision
A snapshot identity is derived from the ordered accepted-record set, record
hashes, partition plan, snapshot format version, and SDK contract version.
Build time, machine identity, process identity, and filesystem location do not
participate in snapshot identity.
Existing snapshots are never overwritten. Corrections create new snapshots.
## Consequences
The same verified record set and implementation contract resolve to the same
snapshot identifier.
Snapshot verification includes every partition hash and the deterministic
logical-manifest hash.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-010-parquet-corpus-partitions.md <<'EOF'
# ADR-INTEL-010: Normalized snapshot records are stored as Parquet
- Status: Accepted
- Phase: INTEL-P2
## Decision
Snapshot records are partitioned by event class and producer identity, ordered
by canonical record identity, and encoded as Parquet using Zstandard
compression.
Parquet files contain normalized corpus metadata and content hashes. They do
not contain producer source code, raw logs, credentials, or absolute paths.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-011-duckdb-is-derived.md <<'EOF'
# ADR-INTEL-011: DuckDB is a derived analytical projection
- Status: Accepted
- Phase: INTEL-P2
## Decision
DuckDB reads immutable snapshot Parquet partitions and exposes a deterministic
`corpus_records` view.
DuckDB files are rebuildable projections. They are not the corpus authority and
must not mutate source snapshot partitions.
EOF
python3 - <<'PY'
from pathlib import Path
path = Path(".l9/architecture.yaml")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "phase: INTEL-P1",
    "phase: INTEL-P2",
    1,
)
old = """phase_2:
  name: reproducible-ingestion
  status: implemented
  includes:
    - append-only ingestion ledger
    - deterministic normalization
    - content-addressed corpus identity
    - redaction inspection
    - quarantine persistence
    - accepted record persistence
    - deterministic duplicate handling
    - store verification
  excludes:
    - immutable corpus snapshots
    - Parquet partitions
    - DuckDB analytics
    - recurrence analysis
    - rule compilation
    - defense-pack publication
"""
new = """phase_2:
  name: reproducible-ingestion
  status: implemented
phase_3:
  name: immutable-snapshots
  status: implemented
  includes:
    - deterministic snapshot planning
    - immutable Parquet partitions
    - corpus snapshot manifests
    - source record set hashes
    - partition integrity hashes
    - snapshot verification
    - derived DuckDB analytical projection
  excludes:
    - recurrence analysis
    - co-occurrence analysis
    - effort modelling
    - rule effectiveness analysis
    - candidate-rule generation
    - defense-pack compilation
    - signing and publication
"""
if old not in text:
    raise SystemExit("unexpected INTEL-P1 architecture block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
python3 - <<'PY'
from pathlib import Path
path = Path("ROADMAP.md")
text = path.read_text(encoding="utf-8")
old = """## INTEL-P2 — Immutable snapshots
Not authorized.
"""
new = """## INTEL-P2 — Immutable snapshots
Implemented:
- verified ingestion-store input;
- deterministic snapshot identity;
- immutable Parquet partitions;
- content-addressed snapshot directories;
- partition and record-set hashing;
- deterministic logical manifests;
- snapshot tamper detection;
- derived DuckDB analytical projection.
DuckDB is a rebuildable projection and is not corpus authority.
"""
if old not in text:
    raise SystemExit("unexpected ROADMAP INTEL-P2 block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
cat >> AGENTS.md <<'EOF'
## INTEL-P2 snapshot rules
- Verify the ingestion store before snapshot construction.
- Sort records by canonical record identity.
- Exclude build time and machine state from snapshot identity.
- Never overwrite an existing snapshot.
- Hash every partition.
- Preserve the source record set hash.
- Treat DuckDB as a rebuildable projection.
- Keep analytics metrics and rule compilation outside this phase.
- Never place source content, raw logs, secrets, or absolute paths in Parquet.
EOF
python -m pip install \
  --disable-pip-version-check \
  --no-input \
  -e ".[dev]"
python -m pip install \
  --disable-pip-version-check \
  --no-input \
  -r requirements/snapshot.txt
python -m pytest \
  tests/architecture \
  tests/contracts \
  tests/ingestion \
  tests/snapshots
workspace="$(mktemp -d)"
trap 'rm -rf "$workspace"' EXIT
ingestion="${workspace}/ingestion"
snapshots="${workspace}/snapshots"
database="${workspace}/analytics/corpus.duckdb"
l9-intelligence ingest-event \
  tests/fixtures/producers/valid-core-gate.json \
  --storage-root "$ingestion" \
  --output "${workspace}/ingestion-result.json"
l9-intelligence build-snapshot \
  --storage-root "$ingestion" \
  --snapshots-root "$snapshots" \
  --output "${workspace}/snapshot-result.json"
snapshot_id="$(
  python - "${workspace}/snapshot-result.json" <<'PY'
import json
import sys
from pathlib import Path
value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)
print(value["snapshot_id"])
PY
)"
snapshot_path="${snapshots}/${snapshot_id}"
l9-intelligence verify-snapshot \
  "$snapshot_path" \
  --output "${workspace}/snapshot-verification.json"
l9-intelligence create-duckdb-projection \
  "$snapshot_path" \
  --database "$database" \
  --output "${workspace}/duckdb-result.json"
python - "$workspace" "$database" <<'PY'
import json
import sys
from pathlib import Path
import duckdb
workspace = Path(sys.argv[1])
database = Path(sys.argv[2])
snapshot = json.loads(
    (workspace / "snapshot-result.json").read_text(
        encoding="utf-8"
    )
)
verification = json.loads(
    (workspace / "snapshot-verification.json").read_text(
        encoding="utf-8"
    )
)
assert verification["status"] == "valid", verification
assert verification["snapshot_id"] == snapshot["snapshot_id"]
assert verification["record_count"] == 1
assert verification["partition_count"] == 1
connection = duckdb.connect(
    str(database),
    read_only=True,
)
try:
    count = connection.execute(
        "SELECT COUNT(*) FROM corpus_records"
    ).fetchone()[0]
finally:
    connection.close()
assert count == 1, count
PY
printf '\nINTEL-P2 immutable snapshots built and validated.\n'
printf 'Snapshot: %s\n' "$snapshot_id"

Execute it:

chmod +x build-phase-3.sh
./build-phase-3.sh

Review and commit:

git status --short
git diff --check
git add \
  .l9 \
  .github/workflows/phase-3-snapshots.yml \
  requirements/snapshot.txt \
  schemas/intelligence \
  src/l9_debt_intelligence \
  tests/architecture \
  tests/snapshots \
  docs/architecture/ADRs \
  AGENTS.md \
  ROADMAP.md
git commit -m "feat!: implement Intelligence INTEL-P2 immutable snapshots"

The resulting boundary is:

verified ingestion store
        ↓
ordered accepted records
        ↓
deterministic partition plan
        ↓
immutable Parquet partitions
        ↓
content-addressed snapshot manifest
        ↓
snapshot verification
        ↓
optional DuckDB projection

Still excluded are recurrence, co-occurrence, effort modelling, rule effectiveness, candidate-rule generation, defense-pack compilation, signing, and release publication. Those begin in INTEL-P3: learning metrics.