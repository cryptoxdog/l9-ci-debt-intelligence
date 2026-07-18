The next phase is INTEL-P1: reproducible ingestion.

It adds:

producer event
    ↓
envelope validation
    ↓
producer compatibility
    ↓
redaction inspection
    ↓
deterministic normalization
    ↓
content-addressed deduplication
    ↓
append-only ingestion ledger
    ├── accepted records
    └── quarantine records

This follows the Intelligence specification’s required ingestion lifecycle: validation, redaction, normalization, deterministic deduplication, quarantine, explicit unknown handling, and immutable correction-oriented history. repo-spec.yaml

Save this as build-phase-2.sh in the Phase 1 repository.

#!/usr/bin/env bash
set -euo pipefail
require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    printf 'INTEL-P1 requires Phase 1 file: %s\n' "$path" >&2
    exit 1
  fi
}
require_file ".l9/architecture.yaml"
require_file ".l9/producer-compatibility.json"
require_file "schemas/intelligence/corpus-event.schema.json"
require_file "schemas/intelligence/corpus-record.schema.json"
require_file "src/l9_debt_intelligence/contracts/validator.py"
mkdir -p \
  .github/workflows \
  docs/architecture/ADRs \
  schemas/intelligence \
  src/l9_debt_intelligence/ingestion \
  tests/ingestion \
  tests/fixtures/ingestion
cat > .l9/ingestion-contract.yaml <<'EOF'
schema: l9.intelligence-ingestion-contract/v1
metadata:
  repository: Quantum-L9/l9-ci-debt-intelligence
  phase: INTEL-P1
  status: authoritative
pipeline:
  - receive
  - validate_envelope
  - validate_producer_compatibility
  - inspect_redaction
  - normalize
  - calculate_identity
  - deduplicate
  - append_ledger
  - persist_record_or_quarantine
determinism:
  canonical_serialization:
    encoding: UTF-8
    object_keys: lexicographic
    whitespace: none
    floating_point_nan: prohibited
  record_identity:
    algorithm: SHA-256
    prefix: cr_
    inputs:
      - producer_id
      - producer_contract
      - event_class
      - snapshot_or_run_id
      - normalized_payload_hash
  duplicate_rule: >
    Events with the same deterministic record identity resolve to the same
    corpus record and create a duplicate-observation ledger entry.
storage:
  phase_1_backend: local-filesystem
  authority: bootstrap-only
  layout:
    ledger: var/intelligence/ledger/events.jsonl
    accepted: var/intelligence/records
    quarantine: var/intelligence/quarantine
    indexes: var/intelligence/indexes
  future_target:
    raw_events: versioned-object-storage
    normalized_records: Parquet
    analytics: DuckDB
  rule: >
    The bootstrap filesystem backend implements the protocol but is not the
    final authoritative fleet storage architecture.
redaction:
  prohibited_content:
    - secret values
    - private keys
    - authorization headers
    - access tokens
    - passwords
    - absolute filesystem paths
    - unredacted raw logs
  behavior:
    safe: continue
    suspected_sensitive_content: quarantine
    explicitly_unredacted: quarantine
  source_content_default: excluded
quarantine:
  reasons:
    - invalid_schema
    - incompatible_schema_version
    - unknown_producer
    - incompatible_producer_contract
    - incompatible_sdk_contract
    - missing_lineage
    - sensitive_content
    - redaction_required
    - fingerprint_collision
    - malformed_event
  invariants:
    - quarantine records preserve the original event hash
    - quarantine records contain no fabricated replacement fields
    - quarantine does not create an accepted corpus record
    - repeated quarantine observations are idempotent
corrections:
  behavior: append-only
  prohibited:
    - silent record overwrite
    - in-place historical mutation
    - deletion without retraction event
phase_2:
  includes:
    - deterministic normalization
    - content-addressed record identity
    - append-only ingestion ledger
    - accepted record persistence
    - quarantine persistence
    - redaction inspection
    - deterministic duplicate handling
    - ingestion CLI
  excludes:
    - Parquet corpus snapshots
    - DuckDB analytics
    - recurrence analysis
    - co-occurrence analysis
    - effort modelling
    - candidate rule generation
    - defense-pack compilation
    - artifact signing
EOF
cat > schemas/intelligence/ingestion-ledger-entry.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/ingestion-ledger-entry/v1",
  "title": "L9 Intelligence Ingestion Ledger Entry",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "sequence",
    "observation_id",
    "event_id",
    "event_hash",
    "producer_id",
    "event_class",
    "disposition",
    "observed_at",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.ingestion-ledger-entry/v1"
    },
    "sequence": {
      "type": "integer",
      "minimum": 1
    },
    "observation_id": {
      "type": "string",
      "pattern": "^obs_[0-9a-f]{64}$"
    },
    "event_id": {
      "type": "string",
      "minLength": 1
    },
    "event_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "producer_id": {
      "type": "string",
      "minLength": 1
    },
    "event_class": {
      "type": "string",
      "minLength": 1
    },
    "record_id": {
      "type": ["string", "null"],
      "pattern": "^cr_[0-9a-f]{64}$"
    },
    "disposition": {
      "enum": [
        "accepted",
        "duplicate",
        "quarantined",
        "rejected"
      ]
    },
    "quarantine_reason": {
      "type": ["string", "null"]
    },
    "observed_at": {
      "type": "string",
      "format": "date-time"
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
cat > schemas/intelligence/quarantine-record.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/quarantine-record/v1",
  "title": "L9 Intelligence Quarantine Record",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "quarantine_id",
    "event_id",
    "event_hash",
    "producer_id",
    "event_class",
    "reason",
    "observed_at",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.quarantine-record/v1"
    },
    "quarantine_id": {
      "type": "string",
      "pattern": "^qr_[0-9a-f]{64}$"
    },
    "event_id": {
      "type": "string"
    },
    "event_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "producer_id": {
      "type": "string"
    },
    "event_class": {
      "type": "string"
    },
    "reason": {
      "enum": [
        "invalid_schema",
        "incompatible_schema_version",
        "unknown_producer",
        "incompatible_producer_contract",
        "incompatible_sdk_contract",
        "missing_lineage",
        "sensitive_content",
        "redaction_required",
        "fingerprint_collision",
        "malformed_event"
      ]
    },
    "observed_at": {
      "type": "string",
      "format": "date-time"
    },
    "limitations": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "event": {
      "type": "object"
    }
  }
}
EOF
cat > schemas/intelligence/ingestion-result.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/ingestion-result/v1",
  "title": "L9 Intelligence Ingestion Result",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "status",
    "event_id",
    "event_hash",
    "observation_id",
    "ledger_sequence",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.ingestion-result/v1"
    },
    "status": {
      "enum": [
        "accepted",
        "duplicate",
        "quarantined",
        "rejected"
      ]
    },
    "event_id": {
      "type": "string"
    },
    "event_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "record_id": {
      "type": ["string", "null"],
      "pattern": "^cr_[0-9a-f]{64}$"
    },
    "quarantine_id": {
      "type": ["string", "null"],
      "pattern": "^qr_[0-9a-f]{64}$"
    },
    "observation_id": {
      "type": "string",
      "pattern": "^obs_[0-9a-f]{64}$"
    },
    "ledger_sequence": {
      "type": "integer",
      "minimum": 1
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
cat > src/l9_debt_intelligence/ingestion/__init__.py <<'EOF'
"""Deterministic, append-only corpus ingestion."""
EOF
cat > src/l9_debt_intelligence/ingestion/models.py <<'EOF'
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class RedactionAssessment:
    safe: bool
    reason: str | None
    limitations: tuple[str, ...]
@dataclass(frozen=True)
class IngestionResult:
    schema_version: str
    status: str
    event_id: str
    event_hash: str
    record_id: str | None
    quarantine_id: str | None
    observation_id: str
    ledger_sequence: int
    limitations: tuple[str, ...]
    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "event_id": self.event_id,
            "event_hash": self.event_hash,
            "record_id": self.record_id,
            "quarantine_id": self.quarantine_id,
            "observation_id": self.observation_id,
            "ledger_sequence": self.ledger_sequence,
            "limitations": list(self.limitations),
        }
EOF
cat > src/l9_debt_intelligence/ingestion/normalization.py <<'EOF'
from __future__ import annotations
import unicodedata
from typing import Any
from l9_debt_intelligence.contracts.canonical import sha256_document
class NormalizationError(ValueError):
    """An event contains a value unsupported by deterministic normalization."""
def normalize_string(value: str) -> str:
    return unicodedata.normalize("NFC", value)
def normalize_value(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        raise NormalizationError(
            "floating-point values are prohibited in corpus events"
        )
    if isinstance(value, str):
        return normalize_string(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise NormalizationError(
                    "JSON object keys must be strings"
                )
            normalized[normalize_string(key)] = normalize_value(value[key])
        return normalized
    raise NormalizationError(
        f"unsupported event value type: {type(value).__name__}"
    )
def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_value(event)
    if not isinstance(normalized, dict):
        raise NormalizationError("event must normalize to an object")
    limitations = normalized.get("limitations", [])
    if isinstance(limitations, list):
        normalized["limitations"] = sorted(set(limitations))
    unknowns = normalized.get("unknowns", [])
    if isinstance(unknowns, list):
        normalized["unknowns"] = sorted(
            unknowns,
            key=lambda item: (
                str(item.get("field", "")),
                str(item.get("reason", "")),
            ),
        )
    lineage = normalized.get("lineage")
    if isinstance(lineage, dict):
        parents = lineage.get("parent_event_ids", [])
        if isinstance(parents, list):
            lineage["parent_event_ids"] = sorted(set(parents))
    return normalized
def normalized_payload_hash(event: dict[str, Any]) -> str:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        raise NormalizationError("event payload must be an object")
    return sha256_document(normalize_value(payload))
EOF
cat > src/l9_debt_intelligence/ingestion/identity.py <<'EOF'
from __future__ import annotations
import hashlib
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
def namespaced_hash(prefix: str, document: Any) -> str:
    digest = hashlib.sha256(canonical_json(document)).hexdigest()
    return f"{prefix}{digest}"
def record_id(
    *,
    producer_id: str,
    producer_contract: str,
    event_class: str,
    snapshot_or_run_id: str,
    payload_hash: str,
) -> str:
    return namespaced_hash(
        "cr_",
        {
            "event_class": event_class,
            "payload_hash": payload_hash,
            "producer_contract": producer_contract,
            "producer_id": producer_id,
            "snapshot_or_run_id": snapshot_or_run_id,
        },
    )
def quarantine_id(event_hash: str, reason: str) -> str:
    return namespaced_hash(
        "qr_",
        {
            "event_hash": event_hash,
            "reason": reason,
        },
    )
def observation_id(
    *,
    event_hash: str,
    observed_at: str,
    sequence: int,
) -> str:
    return namespaced_hash(
        "obs_",
        {
            "event_hash": event_hash,
            "observed_at": observed_at,
            "sequence": sequence,
        },
    )
EOF
cat > src/l9_debt_intelligence/ingestion/redaction.py <<'EOF'
from __future__ import annotations
import re
from typing import Any
from .models import RedactionAssessment
SENSITIVE_KEY = re.compile(
    r"(?:"
    r"authorization|"
    r"password|"
    r"passwd|"
    r"secret|"
    r"token|"
    r"api[_-]?key|"
    r"private[_-]?key|"
    r"client[_-]?secret"
    r")",
    re.IGNORECASE,
)
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
ABSOLUTE_PATH = re.compile(
    r"(?:"
    r"(?<![A-Za-z0-9_.-])/(?:home|Users|var|tmp|private|opt)/[^\s]+"
    r"|"
    r"(?<![A-Za-z0-9_.-])[A-Za-z]:\\[^\s]+"
    r")"
)
def inspect_value(
    value: Any,
    *,
    path: tuple[str, ...] = (),
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if SENSITIVE_KEY.search(key_text):
                findings.append(
                    f"sensitive-key:{'.'.join(path + (key_text,))}"
                )
            findings.extend(
                inspect_value(
                    child,
                    path=path + (key_text,),
                )
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                inspect_value(
                    child,
                    path=path + (str(index),),
                )
            )
    elif isinstance(value, str):
        for pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                findings.append(
                    f"sensitive-value:{'.'.join(path)}"
                )
                break
        if ABSOLUTE_PATH.search(value):
            findings.append(
                f"absolute-path:{'.'.join(path)}"
            )
    return findings
def assess_redaction(event: dict[str, Any]) -> RedactionAssessment:
    status = event.get("redaction_status")
    if status == "quarantine_required":
        return RedactionAssessment(
            safe=False,
            reason="redaction_required",
            limitations=(
                "producer marked the event as requiring quarantine",
            ),
        )
    findings = sorted(set(inspect_value(event.get("payload", {}))))
    if findings:
        return RedactionAssessment(
            safe=False,
            reason="sensitive_content",
            limitations=tuple(findings),
        )
    return RedactionAssessment(
        safe=True,
        reason=None,
        limitations=(),
    )
EOF
cat > src/l9_debt_intelligence/ingestion/storage.py <<'EOF'
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable
from l9_debt_intelligence.contracts.canonical import canonical_json
class StorageError(RuntimeError):
    """Filesystem ingestion storage failed."""
class FilesystemCorpusStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.ledger_path = self.root / "ledger/events.jsonl"
        self.records_path = self.root / "records"
        self.quarantine_path = self.root / "quarantine"
        self.index_path = self.root / "indexes/record-ids.txt"
    def initialize(self) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.records_path.mkdir(parents=True, exist_ok=True)
        self.quarantine_path.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.ledger_path.touch(exist_ok=True)
        self.index_path.touch(exist_ok=True)
    def next_sequence(self) -> int:
        self.initialize()
        sequence = 0
        with self.ledger_path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    sequence += 1
        return sequence + 1
    def has_record(self, record_id: str) -> bool:
        return (self.records_path / f"{record_id}.json").is_file()
    def read_record(self, record_id: str) -> dict[str, Any] | None:
        path = self.records_path / f"{record_id}.json"
        if not path.is_file():
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise StorageError(f"invalid stored record: {path}")
        return value
    def write_record(self, record: dict[str, Any]) -> None:
        record_id = record.get("record_id")
        if not isinstance(record_id, str):
            raise StorageError("record_id is required")
        destination = self.records_path / f"{record_id}.json"
        self._write_once(destination, record)
        existing = set(self._read_index())
        if record_id not in existing:
            existing.add(record_id)
            self._atomic_write_bytes(
                self.index_path,
                (
                    "\n".join(sorted(existing)) + "\n"
                ).encode("utf-8"),
            )
    def write_quarantine(self, record: dict[str, Any]) -> None:
        quarantine_id = record.get("quarantine_id")
        if not isinstance(quarantine_id, str):
            raise StorageError("quarantine_id is required")
        destination = (
            self.quarantine_path / f"{quarantine_id}.json"
        )
        self._write_once(destination, record)
    def append_ledger(self, entry: dict[str, Any]) -> None:
        self.initialize()
        encoded = canonical_json(entry) + b"\n"
        with self.ledger_path.open("ab") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    def _read_index(self) -> Iterable[str]:
        self.initialize()
        with self.index_path.open("r", encoding="utf-8") as stream:
            for line in stream:
                value = line.strip()
                if value:
                    yield value
    def _write_once(
        self,
        destination: Path,
        document: dict[str, Any],
    ) -> None:
        encoded = canonical_json(document) + b"\n"
        if destination.exists():
            existing = destination.read_bytes()
            if existing != encoded:
                raise StorageError(
                    f"immutable object collision: {destination}"
                )
            return
        self._atomic_write_bytes(destination, encoded)
    @staticmethod
    def _atomic_write_bytes(
        destination: Path,
        content: bytes,
    ) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            dir=destination.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
EOF
cat > src/l9_debt_intelligence/ingestion/service.py <<'EOF'
from __future__ import annotations
import datetime as dt
from pathlib import Path
from typing import Any, Callable
from l9_debt_intelligence.contracts.canonical import sha256_document
from l9_debt_intelligence.contracts.errors import ContractError
from l9_debt_intelligence.contracts.validator import EventValidator
from .identity import (
    observation_id,
    quarantine_id,
    record_id,
)
from .models import IngestionResult
from .normalization import (
    NormalizationError,
    normalize_event,
    normalized_payload_hash,
)
from .redaction import assess_redaction
from .storage import FilesystemCorpusStore, StorageError
Clock = Callable[[], dt.datetime]
def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)
def format_time(value: dt.datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("ingestion clock must return timezone-aware values")
    return value.astimezone(dt.timezone.utc).isoformat().replace(
        "+00:00",
        "Z",
    )
class IngestionService:
    def __init__(
        self,
        *,
        event_schema: Path,
        compatibility_registry: Path,
        storage_root: Path,
        clock: Clock = utc_now,
    ) -> None:
        self.validator = EventValidator(
            event_schema=event_schema,
            compatibility_registry=compatibility_registry,
        )
        self.store = FilesystemCorpusStore(storage_root)
        self.clock = clock
    def ingest(self, event: dict[str, Any]) -> IngestionResult:
        observed_at = format_time(self.clock())
        sequence = self.store.next_sequence()
        try:
            normalized = normalize_event(event)
            event_hash = sha256_document(normalized)
        except (NormalizationError, ValueError) as error:
            return self._quarantine(
                event=event,
                event_hash=sha256_document(event),
                reason="malformed_event",
                limitations=(str(error),),
                observed_at=observed_at,
                sequence=sequence,
            )
        try:
            validation = self.validator.validate(normalized)
        except ContractError as error:
            return self._quarantine(
                event=normalized,
                event_hash=event_hash,
                reason="invalid_schema",
                limitations=(str(error),),
                observed_at=observed_at,
                sequence=sequence,
            )
        if validation.status != "accepted":
            reason = self._map_validation_reason(
                validation.quarantine_reason
            )
            return self._quarantine(
                event=normalized,
                event_hash=event_hash,
                reason=reason,
                limitations=validation.limitations,
                observed_at=observed_at,
                sequence=sequence,
            )
        assessment = assess_redaction(normalized)
        if not assessment.safe:
            return self._quarantine(
                event=normalized,
                event_hash=event_hash,
                reason=assessment.reason or "sensitive_content",
                limitations=(
                    tuple(validation.limitations)
                    + assessment.limitations
                ),
                observed_at=observed_at,
                sequence=sequence,
            )
        payload_hash = normalized_payload_hash(normalized)
        corpus_record_id = record_id(
            producer_id=normalized["producer_id"],
            producer_contract=normalized["producer_contract"],
            event_class=normalized["event_class"],
            snapshot_or_run_id=normalized["snapshot_or_run_id"],
            payload_hash=payload_hash,
        )
        existing = self.store.read_record(corpus_record_id)
        if existing is not None:
            stored_hash = (
                existing.get("payload_reference", {})
                .get("content_hash")
            )
            if stored_hash != payload_hash:
                return self._quarantine(
                    event=normalized,
                    event_hash=event_hash,
                    reason="fingerprint_collision",
                    limitations=(
                        "record identity matched but payload hash differed",
                    ),
                    observed_at=observed_at,
                    sequence=sequence,
                )
            status = "duplicate"
        else:
            record = {
                "schema_version": "l9.corpus-record/v1",
                "record_id": corpus_record_id,
                "source_event_id": normalized["event_id"],
                "producer_id": normalized["producer_id"],
                "event_class": normalized["event_class"],
                "lifecycle_state": "NORMALIZED",
                "redaction_status": normalized["redaction_status"],
                "payload_reference": {
                    "producer_contract": normalized[
                        "producer_contract"
                    ],
                    "sdk_schema_references": [],
                    "content_hash": payload_hash,
                },
                "limitations": normalized.get("limitations", []),
                "superseded_by": None,
            }
            self.store.write_record(record)
            status = "accepted"
        observation = observation_id(
            event_hash=event_hash,
            observed_at=observed_at,
            sequence=sequence,
        )
        self.store.append_ledger(
            {
                "schema_version": "l9.ingestion-ledger-entry/v1",
                "sequence": sequence,
                "observation_id": observation,
                "event_id": normalized["event_id"],
                "event_hash": event_hash,
                "producer_id": normalized["producer_id"],
                "event_class": normalized["event_class"],
                "record_id": corpus_record_id,
                "disposition": status,
                "quarantine_reason": None,
                "observed_at": observed_at,
                "limitations": normalized.get("limitations", []),
            }
        )
        return IngestionResult(
            schema_version="l9.ingestion-result/v1",
            status=status,
            event_id=normalized["event_id"],
            event_hash=event_hash,
            record_id=corpus_record_id,
            quarantine_id=None,
            observation_id=observation,
            ledger_sequence=sequence,
            limitations=tuple(
                normalized.get("limitations", [])
            ),
        )
    def _quarantine(
        self,
        *,
        event: dict[str, Any],
        event_hash: str,
        reason: str,
        limitations: tuple[str, ...],
        observed_at: str,
        sequence: int,
    ) -> IngestionResult:
        event_id = str(event.get("event_id", "unknown"))
        producer_id = str(event.get("producer_id", "unknown"))
        event_class = str(event.get("event_class", "unknown"))
        quarantine_record_id = quarantine_id(
            event_hash,
            reason,
        )
        observation = observation_id(
            event_hash=event_hash,
            observed_at=observed_at,
            sequence=sequence,
        )
        self.store.write_quarantine(
            {
                "schema_version": "l9.quarantine-record/v1",
                "quarantine_id": quarantine_record_id,
                "event_id": event_id,
                "event_hash": event_hash,
                "producer_id": producer_id,
                "event_class": event_class,
                "reason": reason,
                "observed_at": observed_at,
                "limitations": list(limitations),
                "event": event,
            }
        )
        self.store.append_ledger(
            {
                "schema_version": "l9.ingestion-ledger-entry/v1",
                "sequence": sequence,
                "observation_id": observation,
                "event_id": event_id,
                "event_hash": event_hash,
                "producer_id": producer_id,
                "event_class": event_class,
                "record_id": None,
                "disposition": "quarantined",
                "quarantine_reason": reason,
                "observed_at": observed_at,
                "limitations": list(limitations),
            }
        )
        return IngestionResult(
            schema_version="l9.ingestion-result/v1",
            status="quarantined",
            event_id=event_id,
            event_hash=event_hash,
            record_id=None,
            quarantine_id=quarantine_record_id,
            observation_id=observation,
            ledger_sequence=sequence,
            limitations=limitations,
        )
    @staticmethod
    def _map_validation_reason(reason: str | None) -> str:
        mapping = {
            "ProducerCompatibilityError": "unknown_producer",
            "SDKCompatibilityError": "incompatible_sdk_contract",
            "redaction_required": "redaction_required",
        }
        return mapping.get(reason, "incompatible_producer_contract")
EOF
cat > src/l9_debt_intelligence/ingestion/verify.py <<'EOF'
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import sha256_document
from .storage import FilesystemCorpusStore
class LedgerVerificationError(RuntimeError):
    """The ingestion ledger or immutable objects are inconsistent."""
def verify_store(root: Path) -> dict[str, Any]:
    store = FilesystemCorpusStore(root)
    store.initialize()
    entries: list[dict[str, Any]] = []
    with store.ledger_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise LedgerVerificationError(
                    f"ledger line {line_number} is not an object"
                )
            expected_sequence = len(entries) + 1
            if value.get("sequence") != expected_sequence:
                raise LedgerVerificationError(
                    f"ledger sequence gap at line {line_number}"
                )
            entries.append(value)
    accepted = 0
    duplicates = 0
    quarantined = 0
    for entry in entries:
        disposition = entry["disposition"]
        if disposition == "accepted":
            accepted += 1
        elif disposition == "duplicate":
            duplicates += 1
        elif disposition == "quarantined":
            quarantined += 1
        record_id = entry.get("record_id")
        if record_id:
            record = store.read_record(record_id)
            if record is None:
                raise LedgerVerificationError(
                    f"ledger references missing record {record_id}"
                )
    return {
        "schema": "l9.ingestion-verification/v1",
        "status": "valid",
        "ledger_entries": len(entries),
        "accepted": accepted,
        "duplicates": duplicates,
        "quarantined": quarantined,
        "record_count": len(
            list(store.records_path.glob("cr_*.json"))
        ),
        "quarantine_count": len(
            list(store.quarantine_path.glob("qr_*.json"))
        ),
    }
EOF
python3 - <<'PY'
from pathlib import Path
path = Path("src/l9_debt_intelligence/cli.py")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "from .contracts.validator import EventValidator\n",
    """from .contracts.validator import EventValidator
from .ingestion.service import IngestionService
from .ingestion.verify import verify_store
""",
)
text = text.replace(
    """    validate.add_argument("--output", type=Path)
    return parser
""",
    """    validate.add_argument("--output", type=Path)
    ingest = commands.add_parser(
        "ingest-event",
        help="Validate and ingest one producer event.",
    )
    ingest.add_argument("event", type=Path)
    ingest.add_argument(
        "--schema",
        type=Path,
        default=repository_root()
        / "schemas/intelligence/corpus-event.schema.json",
    )
    ingest.add_argument(
        "--registry",
        type=Path,
        default=repository_root()
        / ".l9/producer-compatibility.json",
    )
    ingest.add_argument(
        "--storage-root",
        type=Path,
        required=True,
    )
    ingest.add_argument("--output", type=Path)
    verify = commands.add_parser(
        "verify-store",
        help="Verify the append-only ingestion store.",
    )
    verify.add_argument(
        "--storage-root",
        type=Path,
        required=True,
    )
    verify.add_argument("--output", type=Path)
    return parser
""",
)
old_main = """    if arguments.command != "validate-event":
        return 2
    try:
        event = json.loads(arguments.event.read_text(encoding="utf-8"))
        if not isinstance(event, dict):
            raise ValueError("event must contain a JSON object")
        validator = EventValidator(
            event_schema=arguments.schema,
            compatibility_registry=arguments.registry,
        )
        result = validator.validate(event)
        serialized = (
            json.dumps(
                result.as_dict(),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\\n"
        )
        if arguments.output:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(serialized, encoding="utf-8")
        else:
            sys.stdout.write(serialized)
        return 0 if result.status == "accepted" else 3
    except (OSError, ValueError, ContractError) as error:
        print(f"l9-intelligence: {error}", file=sys.stderr)
        return 2
"""
new_main = """    try:
        if arguments.command == "validate-event":
            event = json.loads(
                arguments.event.read_text(encoding="utf-8")
            )
            if not isinstance(event, dict):
                raise ValueError("event must contain a JSON object")
            validator = EventValidator(
                event_schema=arguments.schema,
                compatibility_registry=arguments.registry,
            )
            result = validator.validate(event)
            document = result.as_dict()
            exit_code = 0 if result.status == "accepted" else 3
        elif arguments.command == "ingest-event":
            event = json.loads(
                arguments.event.read_text(encoding="utf-8")
            )
            if not isinstance(event, dict):
                raise ValueError("event must contain a JSON object")
            service = IngestionService(
                event_schema=arguments.schema,
                compatibility_registry=arguments.registry,
                storage_root=arguments.storage_root,
            )
            result = service.ingest(event)
            document = result.as_dict()
            exit_code = (
                0
                if result.status in {"accepted", "duplicate"}
                else 3
            )
        elif arguments.command == "verify-store":
            document = verify_store(arguments.storage_root)
            exit_code = 0
        else:
            return 2
        serialized = (
            json.dumps(
                document,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\\n"
        )
        if arguments.output:
            arguments.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            arguments.output.write_text(
                serialized,
                encoding="utf-8",
            )
        else:
            sys.stdout.write(serialized)
        return exit_code
    except (OSError, ValueError, ContractError) as error:
        print(f"l9-intelligence: {error}", file=sys.stderr)
        return 2
"""
if old_main not in text:
    raise SystemExit("unexpected CLI implementation")
path.write_text(
    text.replace(old_main, new_main),
    encoding="utf-8",
)
PY
cat > tests/fixtures/ingestion/sensitive-event.json <<'EOF'
{
  "schema_version": "l9.corpus-event/v1",
  "producer_id": "Quantum-L9/l9-ci-core",
  "producer_contract": "l9.core-gate-event/v1",
  "sdk_contract": "l9.integration-contract/v1",
  "event_id": "gate-sensitive-100",
  "event_class": "gate_outcome",
  "event_time": "2026-07-17T12:00:00Z",
  "snapshot_or_run_id": "run-sensitive-100",
  "redaction_status": "producer_redacted",
  "limitations": [],
  "unknowns": [],
  "lineage": {
    "producer_event_hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "parent_event_ids": []
  },
  "payload": {
    "authorization": "Bearer secret-token-value-123456789"
  }
}
EOF
cat > tests/ingestion/test_normalization.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.ingestion.normalization import (
    NormalizationError,
    normalize_event,
    normalized_payload_hash,
)
class NormalizationTests(unittest.TestCase):
    def test_mapping_order_does_not_change_hash(self) -> None:
        first = {
            "payload": {
                "b": 2,
                "a": 1,
            }
        }
        second = {
            "payload": {
                "a": 1,
                "b": 2,
            }
        }
        self.assertEqual(
            normalized_payload_hash(first),
            normalized_payload_hash(second),
        )
    def test_limitations_are_sorted_and_unique(self) -> None:
        event = normalize_event(
            {
                "limitations": ["z", "a", "z"],
                "payload": {},
            }
        )
        self.assertEqual(["a", "z"], event["limitations"])
    def test_float_is_rejected(self) -> None:
        with self.assertRaises(NormalizationError):
            normalize_event(
                {
                    "payload": {
                        "confidence": 0.5,
                    }
                }
            )
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/ingestion/test_redaction.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.ingestion.redaction import (
    assess_redaction,
)
class RedactionTests(unittest.TestCase):
    def test_sensitive_key_is_detected(self) -> None:
        result = assess_redaction(
            {
                "redaction_status": "producer_redacted",
                "payload": {
                    "api_token": "value",
                },
            }
        )
        self.assertFalse(result.safe)
        self.assertEqual("sensitive_content", result.reason)
    def test_absolute_path_is_detected(self) -> None:
        result = assess_redaction(
            {
                "redaction_status": "producer_redacted",
                "payload": {
                    "message": "failed in /home/user/project/main.py",
                },
            }
        )
        self.assertFalse(result.safe)
    def test_safe_reference_is_allowed(self) -> None:
        result = assess_redaction(
            {
                "redaction_status": "producer_redacted",
                "payload": {
                    "artifact_reference": "artifact://run-100",
                },
            }
        )
        self.assertTrue(result.safe)
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/ingestion/test_ingestion_service.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.ingestion.service import IngestionService
from l9_debt_intelligence.ingestion.verify import verify_store
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
class IngestionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.event = json.loads(
            (
                ROOT
                / "tests/fixtures/producers/valid-core-gate.json"
            ).read_text(encoding="utf-8")
        )
    def service(self, storage: Path) -> IngestionService:
        return IngestionService(
            event_schema=(
                ROOT / "schemas/intelligence/corpus-event.schema.json"
            ),
            compatibility_registry=(
                ROOT / ".l9/producer-compatibility.json"
            ),
            storage_root=storage,
            clock=fixed_clock,
        )
    def test_event_is_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory)
            result = self.service(storage).ingest(self.event)
            self.assertEqual("accepted", result.status)
            self.assertIsNotNone(result.record_id)
            record = (
                storage
                / "records"
                / f"{result.record_id}.json"
            )
            self.assertTrue(record.is_file())
    def test_duplicate_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory)
            service = self.service(storage)
            first = service.ingest(self.event)
            second = service.ingest(self.event)
            self.assertEqual("accepted", first.status)
            self.assertEqual("duplicate", second.status)
            self.assertEqual(first.record_id, second.record_id)
            records = list(
                (storage / "records").glob("cr_*.json")
            )
            self.assertEqual(1, len(records))
    def test_sensitive_event_is_quarantined(self) -> None:
        event = json.loads(
            (
                ROOT
                / "tests/fixtures/ingestion/sensitive-event.json"
            ).read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory)
            result = self.service(storage).ingest(event)
            self.assertEqual("quarantined", result.status)
            self.assertIsNotNone(result.quarantine_id)
            self.assertIsNone(result.record_id)
    def test_store_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory)
            service = self.service(storage)
            service.ingest(self.event)
            service.ingest(self.event)
            report = verify_store(storage)
            self.assertEqual("valid", report["status"])
            self.assertEqual(2, report["ledger_entries"])
            self.assertEqual(1, report["accepted"])
            self.assertEqual(1, report["duplicates"])
            self.assertEqual(1, report["record_count"])
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/ingestion/test_storage_immutability.py <<'EOF'
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.ingestion.storage import (
    FilesystemCorpusStore,
    StorageError,
)
class StorageImmutabilityTests(unittest.TestCase):
    def test_record_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = FilesystemCorpusStore(Path(directory))
            first = {
                "record_id": "cr_" + ("a" * 64),
                "value": 1,
            }
            second = {
                "record_id": "cr_" + ("a" * 64),
                "value": 2,
            }
            store.write_record(first)
            with self.assertRaises(StorageError):
                store.write_record(second)
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/architecture/test_ingestion_boundary.py <<'EOF'
from __future__ import annotations
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/ingestion"
class IngestionBoundaryTests(unittest.TestCase):
    def test_ingestion_contains_no_analytics_or_compiler(self) -> None:
        prohibited = (
            "duckdb",
            "parquet",
            "cooccurrence",
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
    def test_ingestion_contract_is_present(self) -> None:
        contract = ROOT / ".l9/ingestion-contract.yaml"
        self.assertTrue(contract.is_file())
        text = contract.read_text(encoding="utf-8")
        self.assertIn("append-only", text)
        self.assertIn("deterministic normalization", text)
        self.assertIn("quarantine persistence", text)
if __name__ == "__main__":
    unittest.main()
EOF
cat > .github/workflows/phase-2-ingestion.yml <<'EOF'
name: Intelligence Phase 2 ingestion
on:
  pull_request:
    paths:
      - ".l9/ingestion-contract.yaml"
      - ".l9/producer-compatibility.json"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/contracts/**"
      - "src/l9_debt_intelligence/ingestion/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/architecture/**"
      - "tests/contracts/**"
      - "tests/ingestion/**"
      - "tests/fixtures/**"
  push:
    branches:
      - main
    paths:
      - ".l9/ingestion-contract.yaml"
      - ".l9/producer-compatibility.json"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/contracts/**"
      - "src/l9_debt_intelligence/ingestion/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/architecture/**"
      - "tests/contracts/**"
      - "tests/ingestion/**"
      - "tests/fixtures/**"
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: intelligence-phase-2-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  ingestion:
    runs-on: ubuntu-latest
    timeout-minutes: 10
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
      - name: Install project
        run: |
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -e ".[dev]"
      - name: Run contract and ingestion tests
        run: |
          python -m pytest \
            tests/architecture \
            tests/contracts \
            tests/ingestion
      - name: Exercise deterministic ingestion
        run: |
          set -euo pipefail
          storage="$(mktemp -d)"
          l9-intelligence ingest-event \
            tests/fixtures/producers/valid-core-gate.json \
            --storage-root "${storage}" \
            --output "${storage}/first.json"
          l9-intelligence ingest-event \
            tests/fixtures/producers/valid-core-gate.json \
            --storage-root "${storage}" \
            --output "${storage}/second.json"
          l9-intelligence verify-store \
            --storage-root "${storage}" \
            --output "${storage}/verification.json"
          python - "${storage}" <<'PY'
          import json
          import sys
          from pathlib import Path
          root = Path(sys.argv[1])
          first = json.loads(
              (root / "first.json").read_text()
          )
          second = json.loads(
              (root / "second.json").read_text()
          )
          verification = json.loads(
              (root / "verification.json").read_text()
          )
          assert first["status"] == "accepted", first
          assert second["status"] == "duplicate", second
          assert first["record_id"] == second["record_id"]
          assert verification["status"] == "valid"
          assert verification["record_count"] == 1
          PY
EOF
cat > docs/architecture/ADRs/ADR-INTEL-006-deterministic-ingestion.md <<'EOF'
# ADR-INTEL-006: Corpus ingestion is deterministic and content-addressed
- Status: Accepted
- Phase: INTEL-P1
## Context
Producer events may be redelivered, reordered, or observed by multiple
ingestion workers. Corpus identity cannot depend on arrival order.
## Decision
Corpus record identity is derived from:
- producer identity;
- producer contract;
- event class;
- snapshot or run identity;
- normalized payload hash.
Repeated observations of the same logical record append ledger entries but do
not create additional corpus records.
## Consequences
Arrival timestamps and ledger sequence numbers identify observations, not
corpus records.
A record identity collision with a different normalized payload is quarantined.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-007-bootstrap-filesystem-store.md <<'EOF'
# ADR-INTEL-007: Phase 2 uses a bootstrap filesystem store
- Status: Accepted
- Phase: INTEL-P1
## Context
The target corpus architecture uses versioned object storage, Parquet, and
DuckDB. Those components belong to INTEL-P2.
## Decision
INTEL-P1 implements the ingestion protocol using an append-only JSONL ledger
and immutable content-addressed JSON objects.
This backend is suitable for contract validation, local operation, and
determinism tests. It is not the final fleet corpus storage system.
## Consequences
Storage interfaces must remain independent of analytics and snapshot formats.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-008-quarantine-before-normalization.md <<'EOF'
# ADR-INTEL-008: Sensitive events are quarantined before corpus inclusion
- Status: Accepted
- Phase: INTEL-P1
## Decision
Events containing suspected credentials, private keys, authorization headers,
absolute local paths, or explicitly unredacted payloads are quarantined.
Quarantine preserves the event hash and limitations but creates no accepted
corpus record.
The ingestion service does not fabricate redacted replacements.
EOF
python3 - <<'PY'
from pathlib import Path
path = Path(".l9/architecture.yaml")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "phase: INTEL-P0",
    "phase: INTEL-P1",
    1,
)
old = """phase_1:
  name: schema-federation
  status: implemented
  includes:
    - SDK schema reference registry
    - producer compatibility registry
    - corpus event envelope
    - corpus record extension
    - correction and retraction contracts
    - deterministic contract validation
    - architecture boundary tests
  excludes:
    - persistent corpus ingestion
    - deduplication engine
    - corpus snapshots
    - analytics
    - candidate-rule generation
    - defense-pack compilation
    - artifact publication
"""
new = """phase_1:
  name: schema-federation
  status: implemented
phase_2:
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
if old not in text:
    raise SystemExit("unexpected Phase 1 architecture block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
python3 - <<'PY'
from pathlib import Path
path = Path("ROADMAP.md")
text = path.read_text(encoding="utf-8")
old = """## INTEL-P1 — Reproducible ingestion
Not authorized:
- ingestion ledger;
- redaction engine;
- quarantine persistence;
- deterministic deduplication;
- producer payload validation adapters.
"""
new = """## INTEL-P1 — Reproducible ingestion
Implemented:
- append-only ingestion ledger;
- deterministic event normalization;
- content-addressed corpus records;
- sensitive-content inspection;
- quarantine persistence;
- accepted-record persistence;
- deterministic duplicate observations;
- ingestion store verification.
The Phase 1 filesystem store is a bootstrap implementation, not the final
fleet storage architecture.
"""
if old not in text:
    raise SystemExit("unexpected ROADMAP INTEL-P1 block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
python3 - <<'PY'
from pathlib import Path
path = Path("AGENTS.md")
text = path.read_text(encoding="utf-8")
addition = """
## INTEL-P1 ingestion rules
- Normalize before calculating corpus identity.
- Never include arrival time in corpus record identity.
- Append every observation to the ledger.
- Store accepted records immutably.
- Quarantine suspected sensitive content.
- Never fabricate a sanitized payload.
- Treat duplicate delivery as an observation, not a new record.
- Treat identity collisions as quarantine events.
- Keep snapshot, analytics, and compiler dependencies out of ingestion.
"""
if "## INTEL-P1 ingestion rules" not in text:
    text += addition
path.write_text(text, encoding="utf-8")
PY
python -m pip install \
  --disable-pip-version-check \
  --no-input \
  -e ".[dev]"
python -m pytest \
  tests/architecture \
  tests/contracts \
  tests/ingestion
temporary_store="$(mktemp -d)"
trap 'rm -rf "$temporary_store"' EXIT
l9-intelligence ingest-event \
  tests/fixtures/producers/valid-core-gate.json \
  --storage-root "$temporary_store" \
  --output "$temporary_store/first-result.json"
l9-intelligence ingest-event \
  tests/fixtures/producers/valid-core-gate.json \
  --storage-root "$temporary_store" \
  --output "$temporary_store/second-result.json"
l9-intelligence verify-store \
  --storage-root "$temporary_store" \
  --output "$temporary_store/verification.json"
python - "$temporary_store" <<'PY'
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
first = json.loads(
    (root / "first-result.json").read_text(encoding="utf-8")
)
second = json.loads(
    (root / "second-result.json").read_text(encoding="utf-8")
)
verification = json.loads(
    (root / "verification.json").read_text(encoding="utf-8")
)
assert first["status"] == "accepted", first
assert second["status"] == "duplicate", second
assert first["record_id"] == second["record_id"], (first, second)
assert verification["status"] == "valid", verification
assert verification["ledger_entries"] == 2, verification
assert verification["accepted"] == 1, verification
assert verification["duplicates"] == 1, verification
assert verification["record_count"] == 1, verification
PY
printf '\nINTEL-P1 reproducible ingestion built and validated.\n'

Execute it:

chmod +x build-phase-2.sh
./build-phase-2.sh

Review and commit:

git status --short
git diff --check
git add \
  .l9 \
  .github/workflows/phase-2-ingestion.yml \
  schemas/intelligence \
  src/l9_debt_intelligence \
  tests/architecture \
  tests/ingestion \
  tests/fixtures/ingestion \
  docs/architecture/ADRs \
  AGENTS.md \
  ROADMAP.md
git commit -m "feat!: implement Intelligence INTEL-P1 reproducible ingestion"

Phase boundary

After this phase, Intelligence can deterministically accept, quarantine, and deduplicate producer events:

same logical event delivered twice
    ↓
one immutable corpus record
    +
two append-only ledger observations

Still excluded:

* Parquet partitions
* DuckDB analytics
* immutable corpus snapshots
* recurrence and co-occurrence analysis
* rule compilation
* defense-pack signing or publication

Those begin in INTEL-P2: immutable snapshots.