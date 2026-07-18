The next phase is INTEL-P3: learning metrics.

The public repository still describes its legacy offense lane as directly generating co-occurrence matrices, effort atlases, and invariants. The new phase replaces that pattern with deterministic analytical reports derived only from verified immutable corpus snapshots. 

INTEL-P3 adds:

verified immutable snapshot
        ↓
normalized analytical observations
        ↓
recurrence report
co-occurrence matrix
effort atlas
false-positive report
repair-effectiveness report
        ↓
deterministic analysis manifest

It does not generate candidate rules, invariants, ast-grep rules, or defense packs. Those remain INTEL-P4 responsibilities. This matches the uploaded repository specification’s learning-metrics phase and its explicit unknown-data rule. repo-spec.yaml

Save this as build-phase-4.sh in the INTEL-P2 repository.

#!/usr/bin/env bash
set -euo pipefail
require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    printf 'INTEL-P3 requires INTEL-P2 file: %s\n' "$path" >&2
    exit 1
  fi
}
require_file ".l9/architecture.yaml"
require_file ".l9/snapshot-contract.yaml"
require_file "schemas/intelligence/corpus-snapshot.schema.json"
require_file "src/l9_debt_intelligence/snapshots/verify.py"
require_file "src/l9_debt_intelligence/snapshots/duckdb_projection.py"
mkdir -p \
  .github/workflows \
  docs/architecture/ADRs \
  schemas/intelligence \
  src/l9_debt_intelligence/analytics \
  tests/analytics \
  tests/fixtures/analytics
cat > .l9/analytics-contract.yaml <<'EOF'
schema: l9.intelligence-analytics-contract/v1
metadata:
  repository: Quantum-L9/l9-ci-debt-intelligence
  phase: INTEL-P3
  status: authoritative
source:
  required:
    - verified immutable corpus snapshot
    - l9.corpus-snapshot/v1 manifest
    - immutable Parquet partitions
  prohibited:
    - mutable ingestion working state
    - raw producer logs
    - source repository checkout
    - unverified working-tree output
principles:
  - Every report identifies its source snapshot.
  - Unknown dimensions remain explicitly unknown.
  - Missing values are never converted to zero.
  - Arrival order does not influence analytical output.
  - Report row order is deterministic.
  - Metrics never silently exclude incompatible records.
  - Analysis does not mutate corpus records or snapshots.
  - Analysis results are derived and rebuildable.
observation:
  required_dimensions:
    - record_id
    - producer_id
    - event_class
    - producer_contract
    - occurrence_scope
    - recurrence_fingerprint
  optional_dimensions:
    - canonical_rule_id
    - repository_identity
    - component
    - remediation_class
    - effort_minutes
    - validation_outcome
    - recurrence_outcome
    - false_positive_disposition
    - pack_version
  unknown_representation: null
metrics:
  recurrence:
    grouping:
      - recurrence_fingerprint
      - event_class
    outputs:
      - occurrence_count
      - distinct_scope_count
      - distinct_producer_count
      - first_scope
      - last_scope
  cooccurrence:
    scope: occurrence_scope
    grouping:
      - left_fingerprint
      - right_fingerprint
    rules:
      - pairs are unordered
      - self-pairs are excluded
      - duplicate fingerprints within one scope count once
    outputs:
      - shared_scope_count
      - left_scope_count
      - right_scope_count
      - jaccard_ratio
  effort:
    unit: minutes
    missing_behavior: explicit_unknown
    outputs:
      - known_observation_count
      - unknown_observation_count
      - total_minutes
      - mean_minutes
      - median_minutes
      - p95_minutes
  false_positive:
    accepted_values:
      - confirmed_false_positive
      - confirmed_true_positive
      - inconclusive
    outputs:
      - confirmed_false_positive_count
      - confirmed_true_positive_count
      - inconclusive_count
      - unknown_count
      - false_positive_ratio
  repair_effectiveness:
    accepted_validation_outcomes:
      - passed
      - failed
      - partial
      - unknown
    outputs:
      - attempt_count
      - successful_count
      - failed_count
      - partial_count
      - unknown_count
      - success_ratio
manifest:
  identity:
    algorithm: SHA-256
    prefix: ar_
    inputs:
      - source_snapshot_id
      - analytics_contract_version
      - deterministic report hashes
  required:
    - analysis_run_id
    - source_snapshot_id
    - observation_count
    - report_hashes
    - deterministic_output_hash
    - limitations
phase_4:
  includes:
    - analytical observation projection
    - recurrence metrics
    - co-occurrence metrics
    - effort metrics
    - false-positive metrics
    - repair-effectiveness metrics
    - deterministic report manifests
    - analytical verification
  excludes:
    - candidate-rule scoring
    - leverage scoring
    - generated invariants
    - ast-grep compilation
    - SDK contract compilation
    - regression-fixture compilation
    - defense-pack compilation
    - signing
    - publication
EOF
cat > schemas/intelligence/learning-observation.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/learning-observation/v1",
  "title": "L9 Intelligence Learning Observation",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "record_id",
    "producer_id",
    "event_class",
    "producer_contract",
    "occurrence_scope",
    "recurrence_fingerprint"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.learning-observation/v1"
    },
    "record_id": {
      "type": "string",
      "pattern": "^cr_[0-9a-f]{64}$"
    },
    "producer_id": {
      "type": "string",
      "minLength": 1
    },
    "event_class": {
      "type": "string",
      "minLength": 1
    },
    "producer_contract": {
      "type": "string",
      "minLength": 1
    },
    "occurrence_scope": {
      "type": "string",
      "minLength": 1
    },
    "recurrence_fingerprint": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "canonical_rule_id": {
      "type": ["string", "null"]
    },
    "repository_identity": {
      "type": ["string", "null"]
    },
    "component": {
      "type": ["string", "null"]
    },
    "remediation_class": {
      "type": ["string", "null"]
    },
    "effort_minutes": {
      "type": ["integer", "null"],
      "minimum": 0
    },
    "validation_outcome": {
      "type": ["string", "null"],
      "enum": [
        "passed",
        "failed",
        "partial",
        "unknown",
        null
      ]
    },
    "false_positive_disposition": {
      "type": ["string", "null"],
      "enum": [
        "confirmed_false_positive",
        "confirmed_true_positive",
        "inconclusive",
        null
      ]
    },
    "pack_version": {
      "type": ["string", "null"]
    }
  }
}
EOF
cat > schemas/intelligence/recurrence-report.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/recurrence-report/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "source_snapshot_id",
    "rows",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.recurrence-report/v1"
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "rows": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "recurrence_fingerprint",
          "event_class",
          "occurrence_count",
          "distinct_scope_count",
          "distinct_producer_count",
          "first_scope",
          "last_scope"
        ],
        "properties": {
          "recurrence_fingerprint": {
            "type": "string",
            "pattern": "^[0-9a-f]{64}$"
          },
          "event_class": {
            "type": "string"
          },
          "occurrence_count": {
            "type": "integer",
            "minimum": 1
          },
          "distinct_scope_count": {
            "type": "integer",
            "minimum": 1
          },
          "distinct_producer_count": {
            "type": "integer",
            "minimum": 1
          },
          "first_scope": {
            "type": "string"
          },
          "last_scope": {
            "type": "string"
          }
        }
      }
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
cat > schemas/intelligence/cooccurrence-matrix.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/cooccurrence-matrix/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "source_snapshot_id",
    "rows",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.cooccurrence-matrix/v1"
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "rows": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "left_fingerprint",
          "right_fingerprint",
          "shared_scope_count",
          "left_scope_count",
          "right_scope_count",
          "jaccard_ratio"
        ],
        "properties": {
          "left_fingerprint": {
            "type": "string",
            "pattern": "^[0-9a-f]{64}$"
          },
          "right_fingerprint": {
            "type": "string",
            "pattern": "^[0-9a-f]{64}$"
          },
          "shared_scope_count": {
            "type": "integer",
            "minimum": 1
          },
          "left_scope_count": {
            "type": "integer",
            "minimum": 1
          },
          "right_scope_count": {
            "type": "integer",
            "minimum": 1
          },
          "jaccard_ratio": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      }
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
cat > schemas/intelligence/effort-atlas.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/effort-atlas/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "source_snapshot_id",
    "rows",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.effort-atlas/v1"
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "rows": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "event_class",
          "remediation_class",
          "known_observation_count",
          "unknown_observation_count",
          "total_minutes",
          "mean_minutes",
          "median_minutes",
          "p95_minutes"
        ],
        "properties": {
          "event_class": {
            "type": "string"
          },
          "remediation_class": {
            "type": ["string", "null"]
          },
          "known_observation_count": {
            "type": "integer",
            "minimum": 0
          },
          "unknown_observation_count": {
            "type": "integer",
            "minimum": 0
          },
          "total_minutes": {
            "type": ["integer", "null"],
            "minimum": 0
          },
          "mean_minutes": {
            "type": ["number", "null"],
            "minimum": 0
          },
          "median_minutes": {
            "type": ["number", "null"],
            "minimum": 0
          },
          "p95_minutes": {
            "type": ["number", "null"],
            "minimum": 0
          }
        }
      }
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
cat > schemas/intelligence/rule-effectiveness.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/rule-effectiveness/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "source_snapshot_id",
    "rows",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.rule-effectiveness/v1"
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "rows": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "canonical_rule_id",
          "confirmed_false_positive_count",
          "confirmed_true_positive_count",
          "inconclusive_count",
          "unknown_count",
          "false_positive_ratio",
          "attempt_count",
          "successful_count",
          "failed_count",
          "partial_count",
          "validation_unknown_count",
          "success_ratio"
        ],
        "properties": {
          "canonical_rule_id": {
            "type": ["string", "null"]
          },
          "confirmed_false_positive_count": {
            "type": "integer",
            "minimum": 0
          },
          "confirmed_true_positive_count": {
            "type": "integer",
            "minimum": 0
          },
          "inconclusive_count": {
            "type": "integer",
            "minimum": 0
          },
          "unknown_count": {
            "type": "integer",
            "minimum": 0
          },
          "false_positive_ratio": {
            "type": ["number", "null"],
            "minimum": 0,
            "maximum": 1
          },
          "attempt_count": {
            "type": "integer",
            "minimum": 0
          },
          "successful_count": {
            "type": "integer",
            "minimum": 0
          },
          "failed_count": {
            "type": "integer",
            "minimum": 0
          },
          "partial_count": {
            "type": "integer",
            "minimum": 0
          },
          "validation_unknown_count": {
            "type": "integer",
            "minimum": 0
          },
          "success_ratio": {
            "type": ["number", "null"],
            "minimum": 0,
            "maximum": 1
          }
        }
      }
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
cat > schemas/intelligence/analysis-manifest.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/analysis-manifest/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "analysis_run_id",
    "source_snapshot_id",
    "observation_count",
    "report_hashes",
    "deterministic_output_hash",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.analysis-manifest/v1"
    },
    "analysis_run_id": {
      "type": "string",
      "pattern": "^ar_[0-9a-f]{64}$"
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "observation_count": {
      "type": "integer",
      "minimum": 0
    },
    "report_hashes": {
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$"
      }
    },
    "deterministic_output_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
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
cat > src/l9_debt_intelligence/analytics/__init__.py <<'EOF'
"""Deterministic learning metrics over immutable snapshots."""
EOF
cat > src/l9_debt_intelligence/analytics/errors.py <<'EOF'
class AnalyticsError(RuntimeError):
    """Base error for deterministic Intelligence analytics."""
class AnalyticsVerificationError(AnalyticsError):
    """An analytical output failed integrity verification."""
EOF
cat > src/l9_debt_intelligence/analytics/models.py <<'EOF'
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class LearningObservation:
    record_id: str
    producer_id: str
    event_class: str
    producer_contract: str
    occurrence_scope: str
    recurrence_fingerprint: str
    canonical_rule_id: str | None = None
    repository_identity: str | None = None
    component: str | None = None
    remediation_class: str | None = None
    effort_minutes: int | None = None
    validation_outcome: str | None = None
    false_positive_disposition: str | None = None
    pack_version: str | None = None
    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "l9.learning-observation/v1",
            "record_id": self.record_id,
            "producer_id": self.producer_id,
            "event_class": self.event_class,
            "producer_contract": self.producer_contract,
            "occurrence_scope": self.occurrence_scope,
            "recurrence_fingerprint": self.recurrence_fingerprint,
            "canonical_rule_id": self.canonical_rule_id,
            "repository_identity": self.repository_identity,
            "component": self.component,
            "remediation_class": self.remediation_class,
            "effort_minutes": self.effort_minutes,
            "validation_outcome": self.validation_outcome,
            "false_positive_disposition": (
                self.false_positive_disposition
            ),
            "pack_version": self.pack_version,
        }
EOF
cat > src/l9_debt_intelligence/analytics/projection.py <<'EOF'
from __future__ import annotations
import hashlib
from pathlib import Path
import pyarrow.parquet as pq
from .models import LearningObservation
from l9_debt_intelligence.snapshots.verify import verify_snapshot
def fallback_scope(record_id: str) -> str:
    return f"record:{record_id}"
def load_observations(
    snapshot_path: Path,
) -> tuple[LearningObservation, ...]:
    verification = verify_snapshot(snapshot_path)
    snapshot_path = snapshot_path.resolve()
    observations: list[LearningObservation] = []
    manifest_path = snapshot_path / "manifest.json"
    import json
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    for partition in manifest["partitions"]:
        table = pq.read_table(
            snapshot_path / partition["relative_path"]
        )
        columns = set(table.column_names)
        for row in table.to_pylist():
            record_id = str(row["record_id"])
            payload_hash = str(row["payload_content_hash"])
            occurrence_scope = row.get("occurrence_scope")
            if not isinstance(occurrence_scope, str) or not occurrence_scope:
                occurrence_scope = fallback_scope(record_id)
            fingerprint = row.get("recurrence_fingerprint")
            if not isinstance(fingerprint, str) or len(fingerprint) != 64:
                fingerprint = hashlib.sha256(
                    (
                        str(row["event_class"])
                        + "\0"
                        + payload_hash
                    ).encode("utf-8")
                ).hexdigest()
            effort = row.get("effort_minutes")
            if not isinstance(effort, int) or effort < 0:
                effort = None
            observations.append(
                LearningObservation(
                    record_id=record_id,
                    producer_id=str(row["producer_id"]),
                    event_class=str(row["event_class"]),
                    producer_contract=str(row["producer_contract"]),
                    occurrence_scope=occurrence_scope,
                    recurrence_fingerprint=fingerprint,
                    canonical_rule_id=(
                        row.get("canonical_rule_id")
                        if "canonical_rule_id" in columns
                        else None
                    ),
                    repository_identity=(
                        row.get("repository_identity")
                        if "repository_identity" in columns
                        else None
                    ),
                    component=(
                        row.get("component")
                        if "component" in columns
                        else None
                    ),
                    remediation_class=(
                        row.get("remediation_class")
                        if "remediation_class" in columns
                        else None
                    ),
                    effort_minutes=effort,
                    validation_outcome=(
                        row.get("validation_outcome")
                        if "validation_outcome" in columns
                        else None
                    ),
                    false_positive_disposition=(
                        row.get("false_positive_disposition")
                        if "false_positive_disposition" in columns
                        else None
                    ),
                    pack_version=(
                        row.get("pack_version")
                        if "pack_version" in columns
                        else None
                    ),
                )
            )
    return tuple(
        sorted(
            observations,
            key=lambda item: item.record_id,
        )
    )
EOF
cat > src/l9_debt_intelligence/analytics/metrics.py <<'EOF'
from __future__ import annotations
import math
from collections import defaultdict
from itertools import combinations
from statistics import mean, median
from typing import Iterable
from .models import LearningObservation
def percentile_95(values: list[int]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return float(ordered[rank])
def recurrence_rows(
    observations: Iterable[LearningObservation],
) -> list[dict[str, object]]:
    groups: dict[
        tuple[str, str],
        list[LearningObservation],
    ] = defaultdict(list)
    for item in observations:
        groups[
            (item.recurrence_fingerprint, item.event_class)
        ].append(item)
    rows: list[dict[str, object]] = []
    for fingerprint, event_class in sorted(groups):
        members = groups[(fingerprint, event_class)]
        scopes = sorted(
            {item.occurrence_scope for item in members}
        )
        producers = {
            item.producer_id for item in members
        }
        rows.append(
            {
                "recurrence_fingerprint": fingerprint,
                "event_class": event_class,
                "occurrence_count": len(members),
                "distinct_scope_count": len(scopes),
                "distinct_producer_count": len(producers),
                "first_scope": scopes[0],
                "last_scope": scopes[-1],
            }
        )
    return rows
def cooccurrence_rows(
    observations: Iterable[LearningObservation],
) -> list[dict[str, object]]:
    scope_fingerprints: dict[str, set[str]] = defaultdict(set)
    for item in observations:
        scope_fingerprints[item.occurrence_scope].add(
            item.recurrence_fingerprint
        )
    fingerprint_scopes: dict[str, set[str]] = defaultdict(set)
    pair_scopes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for scope, fingerprints in scope_fingerprints.items():
        ordered = sorted(fingerprints)
        for fingerprint in ordered:
            fingerprint_scopes[fingerprint].add(scope)
        for left, right in combinations(ordered, 2):
            pair_scopes[(left, right)].add(scope)
    rows: list[dict[str, object]] = []
    for left, right in sorted(pair_scopes):
        shared = len(pair_scopes[(left, right)])
        left_count = len(fingerprint_scopes[left])
        right_count = len(fingerprint_scopes[right])
        union = left_count + right_count - shared
        rows.append(
            {
                "left_fingerprint": left,
                "right_fingerprint": right,
                "shared_scope_count": shared,
                "left_scope_count": left_count,
                "right_scope_count": right_count,
                "jaccard_ratio": (
                    round(shared / union, 12)
                    if union
                    else 0.0
                ),
            }
        )
    return rows
def effort_rows(
    observations: Iterable[LearningObservation],
) -> list[dict[str, object]]:
    groups: dict[
        tuple[str, str | None],
        list[LearningObservation],
    ] = defaultdict(list)
    for item in observations:
        groups[
            (item.event_class, item.remediation_class)
        ].append(item)
    rows: list[dict[str, object]] = []
    for event_class, remediation_class in sorted(
        groups,
        key=lambda value: (
            value[0],
            value[1] or "",
        ),
    ):
        members = groups[(event_class, remediation_class)]
        known = [
            item.effort_minutes
            for item in members
            if item.effort_minutes is not None
        ]
        unknown_count = len(members) - len(known)
        rows.append(
            {
                "event_class": event_class,
                "remediation_class": remediation_class,
                "known_observation_count": len(known),
                "unknown_observation_count": unknown_count,
                "total_minutes": sum(known) if known else None,
                "mean_minutes": (
                    round(mean(known), 12)
                    if known
                    else None
                ),
                "median_minutes": (
                    float(median(known))
                    if known
                    else None
                ),
                "p95_minutes": percentile_95(known),
            }
        )
    return rows
def effectiveness_rows(
    observations: Iterable[LearningObservation],
) -> list[dict[str, object]]:
    groups: dict[
        str | None,
        list[LearningObservation],
    ] = defaultdict(list)
    for item in observations:
        groups[item.canonical_rule_id].append(item)
    rows: list[dict[str, object]] = []
    for rule_id in sorted(
        groups,
        key=lambda value: value or "",
    ):
        members = groups[rule_id]
        dispositions = [
            item.false_positive_disposition
            for item in members
        ]
        false_positive = dispositions.count(
            "confirmed_false_positive"
        )
        true_positive = dispositions.count(
            "confirmed_true_positive"
        )
        inconclusive = dispositions.count("inconclusive")
        unknown = len(dispositions) - (
            false_positive + true_positive + inconclusive
        )
        classified = false_positive + true_positive
        outcomes = [
            item.validation_outcome for item in members
        ]
        successful = outcomes.count("passed")
        failed = outcomes.count("failed")
        partial = outcomes.count("partial")
        validation_unknown = len(outcomes) - (
            successful + failed + partial
        )
        known_attempts = successful + failed + partial
        rows.append(
            {
                "canonical_rule_id": rule_id,
                "confirmed_false_positive_count": false_positive,
                "confirmed_true_positive_count": true_positive,
                "inconclusive_count": inconclusive,
                "unknown_count": unknown,
                "false_positive_ratio": (
                    round(false_positive / classified, 12)
                    if classified
                    else None
                ),
                "attempt_count": len(members),
                "successful_count": successful,
                "failed_count": failed,
                "partial_count": partial,
                "validation_unknown_count": validation_unknown,
                "success_ratio": (
                    round(successful / known_attempts, 12)
                    if known_attempts
                    else None
                ),
            }
        )
    return rows
EOF
cat > src/l9_debt_intelligence/analytics/builder.py <<'EOF'
from __future__ import annotations
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
from .metrics import (
    cooccurrence_rows,
    effectiveness_rows,
    effort_rows,
    recurrence_rows,
)
from .projection import load_observations
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
    sha256_bytes,
)
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
    if any(
        item.occurrence_scope.startswith("record:")
        for item in observations
    ):
        limitations.append(
            "occurrence_scope unavailable for some records; "
            "record identity was used as a non-cooccurring fallback"
        )
    if any(
        item.canonical_rule_id is None
        for item in observations
    ):
        limitations.append(
            "canonical_rule_id unavailable for some records"
        )
    if any(
        item.effort_minutes is None
        for item in observations
    ):
        limitations.append(
            "effort_minutes unavailable for some records"
        )
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
        "analytics_contract_version": (
            "l9.intelligence-analytics-contract/v1"
        ),
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
        (temporary / "manifest.json").write_bytes(
            canonical_json(manifest) + b"\n"
        )
        if destination.exists():
            existing = json.loads(
                (destination / "manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            if (
                existing.get("deterministic_output_hash")
                != manifest["deterministic_output_hash"]
            ):
                raise RuntimeError(
                    "analysis identity collision with different output"
                )
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
        "manifest_path": (
            destination / "manifest.json"
        ).as_posix(),
        "observation_count": len(observations),
        "deterministic_output_hash": (
            manifest["deterministic_output_hash"]
        ),
    }
EOF
cat > src/l9_debt_intelligence/analytics/verify.py <<'EOF'
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
        raise AnalyticsVerificationError(
            "analysis manifest does not exist"
        )
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    if manifest.get("schema_version") != "l9.analysis-manifest/v1":
        raise AnalyticsVerificationError(
            "unsupported analysis manifest schema"
        )
    if manifest.get("analysis_run_id") != path.name:
        raise AnalyticsVerificationError(
            "analysis directory identity mismatch"
        )
    report_hashes = manifest.get("report_hashes")
    if not isinstance(report_hashes, dict):
        raise AnalyticsVerificationError(
            "report_hashes must be an object"
        )
    for name, filename in REPORT_FILES.items():
        report_path = path / filename
        if not report_path.is_file():
            raise AnalyticsVerificationError(
                f"missing report: {filename}"
            )
        report = json.loads(
            report_path.read_text(encoding="utf-8")
        )
        actual_hash = sha256_bytes(canonical_json(report))
        if actual_hash != report_hashes.get(name):
            raise AnalyticsVerificationError(
                f"report hash mismatch: {filename}"
            )
        if (
            report.get("source_snapshot_id")
            != manifest.get("source_snapshot_id")
        ):
            raise AnalyticsVerificationError(
                f"report snapshot mismatch: {filename}"
            )
    deterministic_document = {
        "analysis_run_id": manifest["analysis_run_id"],
        "source_snapshot_id": manifest["source_snapshot_id"],
        "observation_count": manifest["observation_count"],
        "report_hashes": manifest["report_hashes"],
        "limitations": manifest["limitations"],
    }
    output_hash = sha256_bytes(
        canonical_json(deterministic_document)
    )
    if output_hash != manifest.get("deterministic_output_hash"):
        raise AnalyticsVerificationError(
            "analysis deterministic output hash mismatch"
        )
    return {
        "schema_version": "l9.analysis-verification/v1",
        "status": "valid",
        "analysis_run_id": manifest["analysis_run_id"],
        "source_snapshot_id": manifest["source_snapshot_id"],
        "observation_count": manifest["observation_count"],
        "verified_report_count": len(REPORT_FILES),
        "deterministic_output_hash": output_hash,
    }
EOF
python3 - <<'PY'
from pathlib import Path
path = Path("src/l9_debt_intelligence/cli.py")
text = path.read_text(encoding="utf-8")
anchor = (
    "from .snapshots.verify import verify_snapshot\n"
)
replacement = """from .snapshots.verify import verify_snapshot
from .analytics.builder import build_analytics
from .analytics.verify import verify_analytics
"""
if replacement not in text:
    if anchor not in text:
        raise SystemExit("unexpected CLI import section")
    text = text.replace(anchor, replacement)
parser_anchor = """    projection.add_argument("--output", type=Path)
    return parser
"""
parser_replacement = """    projection.add_argument("--output", type=Path)
    analytics = commands.add_parser(
        "build-analytics",
        help="Build deterministic learning metrics.",
    )
    analytics.add_argument(
        "snapshot",
        type=Path,
    )
    analytics.add_argument(
        "--analytics-root",
        type=Path,
        required=True,
    )
    analytics.add_argument("--output", type=Path)
    verify_analytics_parser = commands.add_parser(
        "verify-analytics",
        help="Verify deterministic analytical reports.",
    )
    verify_analytics_parser.add_argument(
        "analysis",
        type=Path,
    )
    verify_analytics_parser.add_argument("--output", type=Path)
    return parser
"""
if parser_replacement not in text:
    if parser_anchor not in text:
        raise SystemExit("unexpected CLI parser section")
    text = text.replace(parser_anchor, parser_replacement)
dispatcher_anchor = """        elif arguments.command == "create-duckdb-projection":
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
dispatcher_replacement = """        elif arguments.command == "create-duckdb-projection":
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
        elif arguments.command == "build-analytics":
            document = build_analytics(
                snapshot_path=arguments.snapshot,
                analytics_root=arguments.analytics_root,
            )
            exit_code = 0
        elif arguments.command == "verify-analytics":
            document = verify_analytics(arguments.analysis)
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
cat > tests/analytics/test_metrics.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.analytics.metrics import (
    cooccurrence_rows,
    effort_rows,
    effectiveness_rows,
    recurrence_rows,
)
from l9_debt_intelligence.analytics.models import LearningObservation
def observation(
    record: str,
    scope: str,
    fingerprint: str,
    *,
    effort: int | None = None,
    validation: str | None = None,
    disposition: str | None = None,
    rule: str | None = "rule-1",
) -> LearningObservation:
    return LearningObservation(
        record_id="cr_" + record * 64,
        producer_id="producer",
        event_class="repair_attempt",
        producer_contract="contract/v1",
        occurrence_scope=scope,
        recurrence_fingerprint=fingerprint * 64,
        canonical_rule_id=rule,
        remediation_class="configuration",
        effort_minutes=effort,
        validation_outcome=validation,
        false_positive_disposition=disposition,
    )
class MetricTests(unittest.TestCase):
    def test_recurrence_counts_distinct_scopes(self) -> None:
        rows = recurrence_rows(
            [
                observation("a", "run-1", "1"),
                observation("b", "run-1", "1"),
                observation("c", "run-2", "1"),
            ]
        )
        self.assertEqual(1, len(rows))
        self.assertEqual(3, rows[0]["occurrence_count"])
        self.assertEqual(2, rows[0]["distinct_scope_count"])
    def test_cooccurrence_counts_once_per_scope(self) -> None:
        rows = cooccurrence_rows(
            [
                observation("a", "run-1", "1"),
                observation("b", "run-1", "2"),
                observation("c", "run-2", "1"),
                observation("d", "run-2", "2"),
            ]
        )
        self.assertEqual(1, len(rows))
        self.assertEqual(2, rows[0]["shared_scope_count"])
        self.assertEqual(1.0, rows[0]["jaccard_ratio"])
    def test_missing_effort_remains_unknown(self) -> None:
        rows = effort_rows(
            [
                observation("a", "run-1", "1", effort=10),
                observation("b", "run-2", "1", effort=None),
            ]
        )
        self.assertEqual(1, rows[0]["known_observation_count"])
        self.assertEqual(1, rows[0]["unknown_observation_count"])
        self.assertEqual(10, rows[0]["total_minutes"])
    def test_effectiveness_ratios_use_known_values(self) -> None:
        rows = effectiveness_rows(
            [
                observation(
                    "a",
                    "run-1",
                    "1",
                    validation="passed",
                    disposition="confirmed_true_positive",
                ),
                observation(
                    "b",
                    "run-2",
                    "1",
                    validation="failed",
                    disposition="confirmed_false_positive",
                ),
                observation(
                    "c",
                    "run-3",
                    "1",
                ),
            ]
        )
        self.assertEqual(0.5, rows[0]["success_ratio"])
        self.assertEqual(0.5, rows[0]["false_positive_ratio"])
        self.assertEqual(1, rows[0]["validation_unknown_count"])
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/analytics/test_analytics_lifecycle.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.analytics.builder import build_analytics
from l9_debt_intelligence.analytics.verify import verify_analytics
from l9_debt_intelligence.ingestion.service import IngestionService
from l9_debt_intelligence.snapshots.builder import build_snapshot
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
class AnalyticsLifecycleTests(unittest.TestCase):
    def test_analysis_is_reproducible_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ingestion = root / "ingestion"
            snapshots = root / "snapshots"
            analytics = root / "analytics"
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
                storage_root=ingestion,
                clock=fixed_clock,
            )
            service.ingest(event)
            snapshot = build_snapshot(
                storage_root=ingestion,
                snapshots_root=snapshots,
                clock=fixed_clock,
            )
            first = build_analytics(
                snapshot_path=snapshot.snapshot_path,
                analytics_root=analytics,
            )
            second = build_analytics(
                snapshot_path=snapshot.snapshot_path,
                analytics_root=analytics,
            )
            self.assertEqual(
                first["analysis_run_id"],
                second["analysis_run_id"],
            )
            self.assertEqual(
                first["deterministic_output_hash"],
                second["deterministic_output_hash"],
            )
            verification = verify_analytics(
                Path(first["analysis_path"])
            )
            self.assertEqual("valid", verification["status"])
            self.assertEqual(
                4,
                verification["verified_report_count"],
            )
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/analytics/test_unknown_semantics.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.analytics.metrics import (
    effort_rows,
    effectiveness_rows,
)
from l9_debt_intelligence.analytics.models import LearningObservation
class UnknownSemanticsTests(unittest.TestCase):
    def observation(self) -> LearningObservation:
        return LearningObservation(
            record_id="cr_" + ("a" * 64),
            producer_id="producer",
            event_class="gate_outcome",
            producer_contract="contract/v1",
            occurrence_scope="run-1",
            recurrence_fingerprint="b" * 64,
        )
    def test_missing_effort_is_not_zero(self) -> None:
        row = effort_rows([self.observation()])[0]
        self.assertEqual(0, row["known_observation_count"])
        self.assertEqual(1, row["unknown_observation_count"])
        self.assertIsNone(row["total_minutes"])
        self.assertIsNone(row["mean_minutes"])
    def test_missing_outcomes_do_not_produce_ratio(self) -> None:
        row = effectiveness_rows([self.observation()])[0]
        self.assertIsNone(row["false_positive_ratio"])
        self.assertIsNone(row["success_ratio"])
        self.assertEqual(1, row["unknown_count"])
        self.assertEqual(1, row["validation_unknown_count"])
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/architecture/test_analytics_boundary.py <<'EOF'
from __future__ import annotations
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/analytics"
class AnalyticsBoundaryTests(unittest.TestCase):
    def test_analytics_contains_no_compiler_or_publication(self) -> None:
        prohibited = (
            "candidate_rule",
            "generated_invariant",
            "ast_grep",
            "defense_pack",
            "signature",
            "git push",
            "create_release",
            "upload_artifact",
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
    def test_contract_preserves_unknowns(self) -> None:
        contract = (
            ROOT / ".l9/analytics-contract.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Unknown dimensions remain explicitly unknown.",
            contract,
        )
        self.assertIn(
            "Missing values are never converted to zero.",
            contract,
        )
if __name__ == "__main__":
    unittest.main()
EOF
cat > .github/workflows/phase-4-analytics.yml <<'EOF'
name: Intelligence Phase 4 analytics
on:
  pull_request:
    paths:
      - ".l9/analytics-contract.yaml"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/analytics/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/analytics/**"
      - "tests/architecture/**"
  push:
    branches:
      - main
    paths:
      - ".l9/analytics-contract.yaml"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/analytics/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/analytics/**"
      - "tests/architecture/**"
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: intelligence-phase-4-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  analytics:
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
      - name: Install project
        run: |
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -e ".[dev]"
          python -m pip install \
            --disable-pip-version-check \
            --no-input \
            -r requirements/snapshot.txt
      - name: Run complete Phase 1–4 suite
        run: |
          python -m pytest \
            tests/architecture \
            tests/contracts \
            tests/ingestion \
            tests/snapshots \
            tests/analytics
      - name: Exercise analytical lifecycle
        run: |
          set -euo pipefail
          workspace="$(mktemp -d)"
          ingestion="${workspace}/ingestion"
          snapshots="${workspace}/snapshots"
          analytics="${workspace}/analytics"
          l9-intelligence ingest-event \
            tests/fixtures/producers/valid-core-gate.json \
            --storage-root "${ingestion}"
          l9-intelligence build-snapshot \
            --storage-root "${ingestion}" \
            --snapshots-root "${snapshots}" \
            --output "${workspace}/snapshot.json"
          snapshot_id="$(
            python - "${workspace}/snapshot.json" <<'PY'
          import json
          import sys
          from pathlib import Path
          print(
              json.loads(
                  Path(sys.argv[1]).read_text()
              )["snapshot_id"]
          )
          PY
          )"
          l9-intelligence build-analytics \
            "${snapshots}/${snapshot_id}" \
            --analytics-root "${analytics}" \
            --output "${workspace}/analysis.json"
          analysis_path="$(
            python - "${workspace}/analysis.json" <<'PY'
          import json
          import sys
          from pathlib import Path
          print(
              json.loads(
                  Path(sys.argv[1]).read_text()
              )["analysis_path"]
          )
          PY
          )"
          l9-intelligence verify-analytics \
            "${analysis_path}" \
            --output "${workspace}/verification.json"
          python - "${workspace}/verification.json" <<'PY'
          import json
          import sys
          from pathlib import Path
          value = json.loads(
              Path(sys.argv[1]).read_text()
          )
          assert value["status"] == "valid", value
          assert value["verified_report_count"] == 4, value
          PY
EOF
cat > docs/architecture/ADRs/ADR-INTEL-012-snapshot-only-analytics.md <<'EOF'
# ADR-INTEL-012: Learning metrics consume verified snapshots only
- Status: Accepted
- Phase: INTEL-P3
## Decision
Authoritative learning metrics are derived from verified immutable corpus
snapshots.
Analytics does not read mutable ingestion state, raw logs, repository source,
or legacy generated outputs.
## Consequences
Every report identifies one source snapshot and is reproducible from that
snapshot.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-013-explicit-unknown-metrics.md <<'EOF'
# ADR-INTEL-013: Missing analytical dimensions remain unknown
- Status: Accepted
- Phase: INTEL-P3
## Decision
Missing effort, validation outcomes, rule identities, and false-positive
dispositions are represented as null and counted as unknown.
They are never interpreted as zero, failure, success, true-positive, or
false-positive.
## Consequences
Reports contain known and unknown counts, and ratios use only observations with
the required known classifications.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-014-deterministic-cooccurrence.md <<'EOF'
# ADR-INTEL-014: Co-occurrence is scoped and set-based
- Status: Accepted
- Phase: INTEL-P3
## Decision
Two recurrence fingerprints co-occur when both are present in the same
occurrence scope.
Pairs are unordered. Self-pairs are excluded. Repeated observations of one
fingerprint in the same scope count once.
## Consequences
Arrival order and duplicate delivery cannot inflate co-occurrence.
EOF
python3 - <<'PY'
from pathlib import Path
path = Path(".l9/architecture.yaml")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "phase: INTEL-P2",
    "phase: INTEL-P3",
    1,
)
old = """phase_3:
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
new = """phase_3:
  name: immutable-snapshots
  status: implemented
phase_4:
  name: learning-metrics
  status: implemented
  includes:
    - analytical observation projection
    - recurrence analysis
    - co-occurrence analysis
    - effort modelling
    - false-positive analysis
    - repair-effectiveness analysis
    - deterministic analytical manifests
    - analytical integrity verification
  excludes:
    - candidate-rule generation
    - leverage scoring
    - invariant generation
    - ast-grep compilation
    - SDK contract compilation
    - defense-pack compilation
    - signing and publication
"""
if old not in text:
    raise SystemExit("unexpected INTEL-P2 architecture block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
python3 - <<'PY'
from pathlib import Path
path = Path("ROADMAP.md")
text = path.read_text(encoding="utf-8")
old = """## INTEL-P3 — Learning metrics
Not authorized.
"""
new = """## INTEL-P3 — Learning metrics
Implemented:
- deterministic analytical observation projection;
- recurrence reports;
- scoped co-occurrence matrices;
- effort atlases with explicit unknown counts;
- false-positive metrics;
- repair-effectiveness metrics;
- deterministic analysis manifests;
- analytical tamper verification.
Analytical reports are derived only from verified immutable snapshots.
"""
if old not in text:
    raise SystemExit("unexpected ROADMAP INTEL-P3 block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
cat >> AGENTS.md <<'EOF'
## INTEL-P3 analytical rules
- Read only verified immutable snapshots.
- Preserve the source snapshot identity in every report.
- Keep missing values explicitly unknown.
- Never convert missing effort to zero.
- Never infer success or failure from missing outcomes.
- Deduplicate fingerprints within a co-occurrence scope.
- Sort all report rows deterministically.
- Hash every analytical report.
- Do not generate rules, invariants, fixes, or defense packs in analytics.
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
  tests/snapshots \
  tests/analytics
workspace="$(mktemp -d)"
trap 'rm -rf "$workspace"' EXIT
ingestion="${workspace}/ingestion"
snapshots="${workspace}/snapshots"
analytics="${workspace}/analytics"
l9-intelligence ingest-event \
  tests/fixtures/producers/valid-core-gate.json \
  --storage-root "$ingestion"
l9-intelligence build-snapshot \
  --storage-root "$ingestion" \
  --snapshots-root "$snapshots" \
  --output "${workspace}/snapshot.json"
snapshot_id="$(
  python - "${workspace}/snapshot.json" <<'PY'
import json
import sys
from pathlib import Path
print(
    json.loads(
        Path(sys.argv[1]).read_text(encoding="utf-8")
    )["snapshot_id"]
)
PY
)"
l9-intelligence build-analytics \
  "${snapshots}/${snapshot_id}" \
  --analytics-root "$analytics" \
  --output "${workspace}/analysis.json"
analysis_path="$(
  python - "${workspace}/analysis.json" <<'PY'
import json
import sys
from pathlib import Path
print(
    json.loads(
        Path(sys.argv[1]).read_text(encoding="utf-8")
    )["analysis_path"]
)
PY
)"
l9-intelligence verify-analytics \
  "$analysis_path" \
  --output "${workspace}/verification.json"
python - "${workspace}/verification.json" <<'PY'
import json
import sys
from pathlib import Path
verification = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)
assert verification["status"] == "valid", verification
assert verification["verified_report_count"] == 4, verification
PY
printf '\nINTEL-P3 learning metrics built and validated.\n'
printf 'Snapshot: %s\n' "$snapshot_id"
printf 'Analysis: %s\n' "$analysis_path"

Execute it:

chmod +x build-phase-4.sh
./build-phase-4.sh

Review and commit:

git status --short
git diff --check
git add \
  .l9 \
  .github/workflows/phase-4-analytics.yml \
  schemas/intelligence \
  src/l9_debt_intelligence \
  tests/architecture \
  tests/analytics \
  docs/architecture/ADRs \
  AGENTS.md \
  ROADMAP.md
git commit -m "feat!: implement Intelligence INTEL-P3 learning metrics"

Resulting boundary

immutable snapshot
    ↓
learning observations
    ├── recurrence
    ├── co-occurrence
    ├── effort
    ├── false-positive rate
    └── repair effectiveness
    ↓
content-addressed analysis run

A key limitation remains visible: the current INTEL-P2 snapshot rows do not yet carry all producer-specific dimensions such as canonical rule IDs, remediation effort, and validation outcomes. INTEL-P3 therefore reports those fields as unknown rather than inventing values. The next producer-contract evolution should populate these fields before meaningful fleet-level effectiveness decisions are made.

The next phase is INTEL-P4: rule compilation—candidate-rule models, leverage scoring, regression fixtures, ast-grep compilation, and SDK architecture-contract compilation.