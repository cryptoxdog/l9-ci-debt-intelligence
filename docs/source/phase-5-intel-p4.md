The next phase is INTEL-P4: deterministic rule compilation.

The public repository’s legacy pipeline generates invariants and ast-grep rules directly from working-tree corpus outputs. The converged implementation instead compiles prevention candidates only from a verified INTEL-P3 analysis run tied to an immutable corpus snapshot. 

This phase adds candidate-rule modelling, leverage scoring, generated invariants, ast-grep rule compilation, SDK architecture-contract compilation, regression fixtures, and deterministic compiler manifests. It does not sign, promote, publish, or assemble the final l9.debt-defense/v1 distribution pack; those remain INTEL-P5 responsibilities. repo-spec.yaml

Save as build-phase-5.sh.

#!/usr/bin/env bash
set -euo pipefail
require_file() {
  local path="$1"
  [[ -f "$path" ]] || {
    printf 'INTEL-P4 requires INTEL-P3 file: %s\n' "$path" >&2
    exit 1
  }
}
require_file ".l9/architecture.yaml"
require_file ".l9/analytics-contract.yaml"
require_file "schemas/intelligence/analysis-manifest.schema.json"
require_file "src/l9_debt_intelligence/analytics/verify.py"
require_file "src/l9_debt_intelligence/analytics/builder.py"
mkdir -p \
  .github/workflows \
  docs/architecture/ADRs \
  schemas/intelligence \
  src/l9_debt_intelligence/compilation \
  tests/compilation \
  tests/fixtures/compilation
cat > .l9/compiler-contract.yaml <<'EOF'
schema: l9.intelligence-compiler-contract/v1
metadata:
  repository: Quantum-L9/l9-ci-debt-intelligence
  phase: INTEL-P4
  status: authoritative
input:
  required:
    - verified l9.analysis-manifest/v1
    - verified immutable source snapshot
    - recurrence report
    - co-occurrence matrix
    - effort atlas
    - rule-effectiveness report
  prohibited:
    - mutable ingestion state
    - raw logs
    - source repository checkout
    - legacy generated outputs
    - unpublished working-tree corpus
candidate_identity:
  algorithm: SHA-256
  prefix: candidate_
  inputs:
    - source_snapshot_id
    - analysis_run_id
    - recurrence_fingerprint
    - candidate_kind
    - normalized_match_contract
    - normalized_action_contract
scoring:
  scale:
    minimum: 0
    maximum: 5
  dimensions:
    recurrence:
      weight: 0.30
    scope_breadth:
      weight: 0.20
    effort:
      weight: 0.15
    repair_success:
      weight: 0.15
    false_positive_safety:
      weight: 0.20
  thresholds:
    compile: 3.0
    promotion_eligible: 4.0
  unknown_rule: Unknown evidence contributes no positive score.
  prohibition: Unknown evidence is never converted to favorable evidence.
compiler_outputs:
  - candidate rule catalog
  - generated invariants
  - ast-grep rule candidates
  - SDK architecture-contract candidates
  - regression fixtures
  - regression results
  - compiler manifest
determinism:
  - candidate order is canonical
  - YAML key order is stable
  - JSON serialization is canonical
  - compiler timestamps do not participate in artifact identity
  - same inputs and compiler version produce the same output hashes
safety:
  generated_rules:
    state: candidate_only
    blocking_policy: prohibited
    automatic_promotion: prohibited
    external_commands: prohibited
    repository_mutation: prohibited
  required_regression_classes:
    - positive_fixture
    - negative_fixture
    - deterministic_rebuild
    - schema_validation
    - lineage_validation
phase_5:
  includes:
    - candidate extraction
    - leverage scoring
    - generated invariants
    - ast-grep candidate compilation
    - SDK architecture-contract candidate compilation
    - regression fixture compilation
    - regression execution
    - deterministic compiler manifest
  excludes:
    - defense-pack assembly
    - signing
    - release channels
    - promotion
    - retirement
    - Core policy mutation
EOF
cat > schemas/intelligence/candidate-rule.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/candidate-rule/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "candidate_id",
    "source_snapshot_id",
    "analysis_run_id",
    "candidate_kind",
    "recurrence_fingerprint",
    "title",
    "rationale",
    "match_contract",
    "action_contract",
    "score",
    "score_components",
    "state",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.candidate-rule/v1"
    },
    "candidate_id": {
      "type": "string",
      "pattern": "^candidate_[0-9a-f]{64}$"
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "analysis_run_id": {
      "type": "string",
      "pattern": "^ar_[0-9a-f]{64}$"
    },
    "candidate_kind": {
      "enum": [
        "ast_grep",
        "sdk_architecture_contract",
        "generated_invariant"
      ]
    },
    "recurrence_fingerprint": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "rationale": {
      "type": "string",
      "minLength": 1
    },
    "match_contract": {
      "type": "object"
    },
    "action_contract": {
      "type": "object"
    },
    "score": {
      "type": "number",
      "minimum": 0,
      "maximum": 5
    },
    "score_components": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "recurrence",
        "scope_breadth",
        "effort",
        "repair_success",
        "false_positive_safety"
      ],
      "properties": {
        "recurrence": {"type": "number", "minimum": 0, "maximum": 5},
        "scope_breadth": {"type": "number", "minimum": 0, "maximum": 5},
        "effort": {"type": "number", "minimum": 0, "maximum": 5},
        "repair_success": {"type": "number", "minimum": 0, "maximum": 5},
        "false_positive_safety": {
          "type": "number",
          "minimum": 0,
          "maximum": 5
        }
      }
    },
    "state": {
      "enum": [
        "deferred",
        "compiled_candidate",
        "promotion_eligible"
      ]
    },
    "limitations": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true
    }
  }
}
EOF
cat > schemas/intelligence/generated-invariant.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/generated-invariant/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "invariant_id",
    "candidate_id",
    "statement",
    "scope",
    "severity",
    "evidence",
    "state"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.generated-invariant/v1"
    },
    "invariant_id": {
      "type": "string",
      "pattern": "^invariant_[0-9a-f]{64}$"
    },
    "candidate_id": {
      "type": "string",
      "pattern": "^candidate_[0-9a-f]{64}$"
    },
    "statement": {
      "type": "string",
      "minLength": 1
    },
    "scope": {
      "type": "string",
      "minLength": 1
    },
    "severity": {
      "enum": ["info", "warning", "error"]
    },
    "evidence": {
      "type": "object",
      "required": [
        "source_snapshot_id",
        "analysis_run_id",
        "recurrence_fingerprint"
      ]
    },
    "state": {
      "const": "candidate"
    }
  }
}
EOF
cat > schemas/intelligence/compiler-manifest.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/compiler-manifest/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "compilation_id",
    "compiler_version",
    "source_snapshot_id",
    "analysis_run_id",
    "candidate_count",
    "compiled_candidate_count",
    "promotion_eligible_count",
    "artifact_hashes",
    "regression_summary",
    "deterministic_output_hash",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.compiler-manifest/v1"
    },
    "compilation_id": {
      "type": "string",
      "pattern": "^compile_[0-9a-f]{64}$"
    },
    "compiler_version": {
      "type": "string",
      "minLength": 1
    },
    "source_snapshot_id": {
      "type": "string",
      "pattern": "^cs_[0-9a-f]{64}$"
    },
    "analysis_run_id": {
      "type": "string",
      "pattern": "^ar_[0-9a-f]{64}$"
    },
    "candidate_count": {
      "type": "integer",
      "minimum": 0
    },
    "compiled_candidate_count": {
      "type": "integer",
      "minimum": 0
    },
    "promotion_eligible_count": {
      "type": "integer",
      "minimum": 0
    },
    "artifact_hashes": {
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$"
      }
    },
    "regression_summary": {
      "type": "object",
      "required": [
        "fixture_count",
        "passed",
        "failed"
      ]
    },
    "deterministic_output_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "limitations": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true
    }
  }
}
EOF
cat > schemas/intelligence/regression-result.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "l9://intelligence/regression-result/v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "candidate_id",
    "fixture_id",
    "fixture_class",
    "status",
    "expected",
    "observed"
  ],
  "properties": {
    "schema_version": {
      "const": "l9.regression-result/v1"
    },
    "candidate_id": {
      "type": "string"
    },
    "fixture_id": {
      "type": "string"
    },
    "fixture_class": {
      "enum": [
        "positive_fixture",
        "negative_fixture",
        "schema_validation",
        "lineage_validation"
      ]
    },
    "status": {
      "enum": ["passed", "failed"]
    },
    "expected": {},
    "observed": {}
  }
}
EOF
cat > src/l9_debt_intelligence/compilation/__init__.py <<'EOF'
"""Deterministic candidate prevention-rule compilation."""
EOF
cat > src/l9_debt_intelligence/compilation/errors.py <<'EOF'
class CompilationError(RuntimeError):
    """Base error for prevention candidate compilation."""
class CompilationVerificationError(CompilationError):
    """Compiled candidate artifacts failed verification."""
EOF
cat > src/l9_debt_intelligence/compilation/scoring.py <<'EOF'
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class Score:
    recurrence: float
    scope_breadth: float
    effort: float
    repair_success: float
    false_positive_safety: float
    @property
    def total(self) -> float:
        value = (
            self.recurrence * 0.30
            + self.scope_breadth * 0.20
            + self.effort * 0.15
            + self.repair_success * 0.15
            + self.false_positive_safety * 0.20
        )
        return round(min(5.0, max(0.0, value)), 6)
    def as_dict(self) -> dict[str, float]:
        return {
            "recurrence": self.recurrence,
            "scope_breadth": self.scope_breadth,
            "effort": self.effort,
            "repair_success": self.repair_success,
            "false_positive_safety": self.false_positive_safety,
        }
def capped_ratio(value: int | float | None, target: float) -> float:
    if value is None or target <= 0:
        return 0.0
    return round(min(5.0, max(0.0, float(value) / target * 5)), 6)
def calculate_score(
    *,
    occurrence_count: int,
    distinct_scope_count: int,
    mean_effort_minutes: float | None,
    repair_success_ratio: float | None,
    false_positive_ratio: float | None,
) -> Score:
    return Score(
        recurrence=capped_ratio(occurrence_count, 10),
        scope_breadth=capped_ratio(distinct_scope_count, 5),
        effort=capped_ratio(mean_effort_minutes, 120),
        repair_success=(
            round(repair_success_ratio * 5, 6)
            if repair_success_ratio is not None
            else 0.0
        ),
        false_positive_safety=(
            round((1.0 - false_positive_ratio) * 5, 6)
            if false_positive_ratio is not None
            else 0.0
        ),
    )
def candidate_state(score: float) -> str:
    if score >= 4.0:
        return "promotion_eligible"
    if score >= 3.0:
        return "compiled_candidate"
    return "deferred"
EOF
cat > src/l9_debt_intelligence/compilation/candidates.py <<'EOF'
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)
from .scoring import calculate_score, candidate_state
def load_report(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"report must be an object: {path}")
    return value
def index_effectiveness(
    report: dict[str, Any],
) -> dict[str | None, dict[str, Any]]:
    return {
        row.get("canonical_rule_id"): row
        for row in report.get("rows", [])
        if isinstance(row, dict)
    }
def mean_effort_by_event_class(
    report: dict[str, Any],
) -> dict[str, float | None]:
    values: dict[str, list[float]] = {}
    for row in report.get("rows", []):
        if not isinstance(row, dict):
            continue
        event_class = row.get("event_class")
        mean_value = row.get("mean_minutes")
        if not isinstance(event_class, str):
            continue
        values.setdefault(event_class, [])
        if isinstance(mean_value, (int, float)):
            values[event_class].append(float(mean_value))
    return {
        key: (
            round(sum(items) / len(items), 6)
            if items
            else None
        )
        for key, items in values.items()
    }
def extract_candidates(
    analysis_path: Path,
) -> list[dict[str, Any]]:
    manifest = load_report(analysis_path / "manifest.json")
    recurrence = load_report(
        analysis_path / "recurrence-report.json"
    )
    effort = load_report(analysis_path / "effort-atlas.json")
    effectiveness = load_report(
        analysis_path / "rule-effectiveness.json"
    )
    effort_index = mean_effort_by_event_class(effort)
    effectiveness_index = index_effectiveness(effectiveness)
    candidates: list[dict[str, Any]] = []
    for row in recurrence.get("rows", []):
        if not isinstance(row, dict):
            continue
        fingerprint = str(row["recurrence_fingerprint"])
        event_class = str(row["event_class"])
        rule_effectiveness = effectiveness_index.get(None, {})
        score = calculate_score(
            occurrence_count=int(row["occurrence_count"]),
            distinct_scope_count=int(
                row["distinct_scope_count"]
            ),
            mean_effort_minutes=effort_index.get(event_class),
            repair_success_ratio=rule_effectiveness.get(
                "success_ratio"
            ),
            false_positive_ratio=rule_effectiveness.get(
                "false_positive_ratio"
            ),
        )
        candidate_kind = (
            "sdk_architecture_contract"
            if event_class in {
                "gate_outcome",
                "CI_failure_classification",
            }
            else "ast_grep"
        )
        match_contract = {
            "event_class": event_class,
            "recurrence_fingerprint": fingerprint,
        }
        action_contract = {
            "behavior": "diagnose",
            "automatic_fix": False,
            "blocking": False,
        }
        identity = {
            "source_snapshot_id": manifest["source_snapshot_id"],
            "analysis_run_id": manifest["analysis_run_id"],
            "recurrence_fingerprint": fingerprint,
            "candidate_kind": candidate_kind,
            "match_contract": match_contract,
            "action_contract": action_contract,
        }
        candidate_id = namespaced_document_hash(
            "candidate_",
            identity,
        )
        limitations = list(
            sorted(
                set(
                    recurrence.get("limitations", [])
                    + effort.get("limitations", [])
                    + effectiveness.get("limitations", [])
                )
            )
        )
        candidates.append(
            {
                "schema_version": "l9.candidate-rule/v1",
                "candidate_id": candidate_id,
                "source_snapshot_id": manifest[
                    "source_snapshot_id"
                ],
                "analysis_run_id": manifest["analysis_run_id"],
                "candidate_kind": candidate_kind,
                "recurrence_fingerprint": fingerprint,
                "title": (
                    f"Prevent recurring {event_class} pattern "
                    f"{fingerprint[:12]}"
                ),
                "rationale": (
                    f"Observed {row['occurrence_count']} times across "
                    f"{row['distinct_scope_count']} distinct scopes."
                ),
                "match_contract": match_contract,
                "action_contract": action_contract,
                "score": score.total,
                "score_components": score.as_dict(),
                "state": candidate_state(score.total),
                "limitations": limitations,
            }
        )
    return sorted(
        candidates,
        key=lambda item: item["candidate_id"],
    )
EOF
cat > src/l9_debt_intelligence/compilation/emitters.py <<'EOF'
from __future__ import annotations
from typing import Any
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)
def generated_invariant(
    candidate: dict[str, Any],
) -> dict[str, Any]:
    identity = {
        "candidate_id": candidate["candidate_id"],
        "statement": candidate["title"],
    }
    return {
        "schema_version": "l9.generated-invariant/v1",
        "invariant_id": namespaced_document_hash(
            "invariant_",
            identity,
        ),
        "candidate_id": candidate["candidate_id"],
        "statement": candidate["title"],
        "scope": candidate["match_contract"]["event_class"],
        "severity": (
            "warning"
            if candidate["state"] == "promotion_eligible"
            else "info"
        ),
        "evidence": {
            "source_snapshot_id": candidate[
                "source_snapshot_id"
            ],
            "analysis_run_id": candidate["analysis_run_id"],
            "recurrence_fingerprint": candidate[
                "recurrence_fingerprint"
            ],
        },
        "state": "candidate",
    }
def ast_grep_rule(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": candidate["candidate_id"],
        "language": "generic",
        "severity": "warning",
        "message": candidate["title"],
        "rule": {
            "kind": "candidate_placeholder",
            "regex": (
                "L9_CANDIDATE_"
                + candidate["recurrence_fingerprint"][:16]
            ),
        },
        "metadata": {
            "state": "candidate",
            "blocking": False,
            "automatic_fix": False,
            "score": candidate["score"],
            "source_snapshot_id": candidate[
                "source_snapshot_id"
            ],
            "analysis_run_id": candidate["analysis_run_id"],
        },
    }
def sdk_architecture_contract(
    candidate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "l9.sdk-architecture-contract-candidate/v1",
        "contract_id": candidate["candidate_id"],
        "state": "candidate",
        "blocking": False,
        "selector": candidate["match_contract"],
        "expectation": {
            "diagnostic": candidate["title"],
            "automatic_remediation": False,
        },
        "lineage": {
            "source_snapshot_id": candidate[
                "source_snapshot_id"
            ],
            "analysis_run_id": candidate["analysis_run_id"],
            "recurrence_fingerprint": candidate[
                "recurrence_fingerprint"
            ],
        },
    }
def regression_fixtures(
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    prefix = candidate["candidate_id"][-12:]
    return [
        {
            "fixture_id": f"fixture_positive_{prefix}",
            "candidate_id": candidate["candidate_id"],
            "fixture_class": "positive_fixture",
            "input": {
                "event_class": candidate[
                    "match_contract"
                ]["event_class"],
                "recurrence_fingerprint": candidate[
                    "recurrence_fingerprint"
                ],
            },
            "expected_match": True,
        },
        {
            "fixture_id": f"fixture_negative_{prefix}",
            "candidate_id": candidate["candidate_id"],
            "fixture_class": "negative_fixture",
            "input": {
                "event_class": "unrelated_event",
                "recurrence_fingerprint": "0" * 64,
            },
            "expected_match": False,
        },
    ]
EOF
cat > src/l9_debt_intelligence/compilation/regression.py <<'EOF'
from __future__ import annotations
from typing import Any
def evaluate_fixture(
    candidate: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    value = fixture["input"]
    observed = (
        value.get("event_class")
        == candidate["match_contract"].get("event_class")
        and value.get("recurrence_fingerprint")
        == candidate["recurrence_fingerprint"]
    )
    expected = bool(fixture["expected_match"])
    return {
        "schema_version": "l9.regression-result/v1",
        "candidate_id": candidate["candidate_id"],
        "fixture_id": fixture["fixture_id"],
        "fixture_class": fixture["fixture_class"],
        "status": "passed" if observed == expected else "failed",
        "expected": expected,
        "observed": observed,
    }
EOF
cat > src/l9_debt_intelligence/compilation/builder.py <<'EOF'
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
        "source_snapshot_id": verification[
            "source_snapshot_id"
        ],
        "analysis_run_id": verification["analysis_run_id"],
        "candidate_ids": [
            candidate["candidate_id"]
            for candidate in candidates
        ],
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
                artifact_hashes[
                    f"ast-grep/{candidate['candidate_id']}"
                ] = write_yaml(
                    temporary
                    / "ast-grep"
                    / f"{candidate['candidate_id']}.yaml",
                    ast_grep_rule(candidate),
                )
            if (
                candidate["candidate_kind"]
                == "sdk_architecture_contract"
            ):
                artifact_hashes[
                    f"sdk-contracts/{candidate['candidate_id']}"
                ] = write_json(
                    temporary
                    / "sdk-contracts"
                    / f"{candidate['candidate_id']}.json",
                    sdk_architecture_contract(candidate),
                )
            candidate_fixtures = regression_fixtures(candidate)
            fixtures.extend(candidate_fixtures)
            results.extend(
                evaluate_fixture(candidate, fixture)
                for fixture in candidate_fixtures
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
        passed = sum(
            result["status"] == "passed"
            for result in results
        )
        failed = len(results) - passed
        deterministic_document = {
            "compilation_id": compilation_id,
            "compiler_version": COMPILER_VERSION,
            "source_snapshot_id": verification[
                "source_snapshot_id"
            ],
            "analysis_run_id": verification[
                "analysis_run_id"
            ],
            "candidate_count": len(candidates),
            "compiled_candidate_count": sum(
                candidate["state"] != "deferred"
                for candidate in candidates
            ),
            "promotion_eligible_count": sum(
                candidate["state"] == "promotion_eligible"
                for candidate in candidates
            ),
            "artifact_hashes": dict(
                sorted(artifact_hashes.items())
            ),
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
            raise RuntimeError(
                f"{failed} compiler regression fixtures failed"
            )
        if destination.exists():
            existing = json.loads(
                (destination / "manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            if (
                existing["deterministic_output_hash"]
                != manifest["deterministic_output_hash"]
            ):
                raise RuntimeError(
                    "compilation identity collision"
                )
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
        "manifest_path": (
            destination / "manifest.json"
        ).as_posix(),
        "candidate_count": len(candidates),
        "compiled_candidate_count": sum(
            candidate["state"] != "deferred"
            for candidate in candidates
        ),
        "promotion_eligible_count": sum(
            candidate["state"] == "promotion_eligible"
            for candidate in candidates
        ),
        "deterministic_output_hash": manifest[
            "deterministic_output_hash"
        ],
    }
EOF
cat > src/l9_debt_intelligence/compilation/verify.py <<'EOF'
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
        raise CompilationVerificationError(
            "compiler manifest does not exist"
        )
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    if manifest.get("schema_version") != "l9.compiler-manifest/v1":
        raise CompilationVerificationError(
            "unsupported compiler manifest"
        )
    if manifest.get("compilation_id") != path.name:
        raise CompilationVerificationError(
            "compilation directory identity mismatch"
        )
    file_map = {
        "candidates": path / "candidates.json",
        "invariants": path / "generated-invariants.json",
        "regression-fixtures": (
            path / "regression-fixtures.json"
        ),
        "regression-results": (
            path / "regression-results.json"
        ),
    }
    for key, expected_hash in manifest["artifact_hashes"].items():
        artifact = file_map.get(key)
        if artifact is None:
            prefix, candidate_id = key.split("/", 1)
            extension = "yaml" if prefix == "ast-grep" else "json"
            artifact = path / prefix / f"{candidate_id}.{extension}"
        if not artifact.is_file():
            raise CompilationVerificationError(
                f"missing compiler artifact: {key}"
            )
        if artifact.suffix == ".json":
            document = json.loads(
                artifact.read_text(encoding="utf-8")
            )
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
    output_hash = sha256_bytes(
        canonical_json(deterministic_document)
    )
    if output_hash != manifest["deterministic_output_hash"]:
        raise CompilationVerificationError(
            "compiler deterministic hash mismatch"
        )
    if manifest["regression_summary"]["failed"] != 0:
        raise CompilationVerificationError(
            "compiler regressions contain failures"
        )
    return {
        "schema_version": "l9.compilation-verification/v1",
        "status": "valid",
        "compilation_id": manifest["compilation_id"],
        "source_snapshot_id": manifest["source_snapshot_id"],
        "analysis_run_id": manifest["analysis_run_id"],
        "candidate_count": manifest["candidate_count"],
        "verified_artifact_count": len(
            manifest["artifact_hashes"]
        ),
        "deterministic_output_hash": output_hash,
    }
EOF
python3 - <<'PY'
from pathlib import Path
path = Path("src/l9_debt_intelligence/cli.py")
text = path.read_text(encoding="utf-8")
anchor = "from .analytics.verify import verify_analytics\n"
replacement = """from .analytics.verify import verify_analytics
from .compilation.builder import build_compilation
from .compilation.verify import verify_compilation
"""
if replacement not in text:
    if anchor not in text:
        raise SystemExit("unexpected CLI imports")
    text = text.replace(anchor, replacement)
parser_anchor = """    verify_analytics_parser.add_argument("--output", type=Path)
    return parser
"""
parser_replacement = """    verify_analytics_parser.add_argument("--output", type=Path)
    compile_parser = commands.add_parser(
        "compile-candidates",
        help="Compile deterministic prevention candidates.",
    )
    compile_parser.add_argument("analysis", type=Path)
    compile_parser.add_argument(
        "--compilation-root",
        type=Path,
        required=True,
    )
    compile_parser.add_argument("--output", type=Path)
    verify_compile_parser = commands.add_parser(
        "verify-compilation",
        help="Verify candidate compiler outputs.",
    )
    verify_compile_parser.add_argument(
        "compilation",
        type=Path,
    )
    verify_compile_parser.add_argument("--output", type=Path)
    return parser
"""
if parser_replacement not in text:
    if parser_anchor not in text:
        raise SystemExit("unexpected CLI parser")
    text = text.replace(parser_anchor, parser_replacement)
dispatcher_anchor = """        elif arguments.command == "verify-analytics":
            document = verify_analytics(arguments.analysis)
            exit_code = 0
        else:
            return 2
"""
dispatcher_replacement = """        elif arguments.command == "verify-analytics":
            document = verify_analytics(arguments.analysis)
            exit_code = 0
        elif arguments.command == "compile-candidates":
            document = build_compilation(
                analysis_path=arguments.analysis,
                compilation_root=arguments.compilation_root,
            )
            exit_code = 0
        elif arguments.command == "verify-compilation":
            document = verify_compilation(
                arguments.compilation
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
cat > tests/compilation/test_scoring.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.compilation.scoring import (
    calculate_score,
    candidate_state,
)
class ScoringTests(unittest.TestCase):
    def test_unknowns_provide_no_positive_score(self) -> None:
        score = calculate_score(
            occurrence_count=0,
            distinct_scope_count=0,
            mean_effort_minutes=None,
            repair_success_ratio=None,
            false_positive_ratio=None,
        )
        self.assertEqual(0.0, score.total)
    def test_high_evidence_is_promotion_eligible(self) -> None:
        score = calculate_score(
            occurrence_count=10,
            distinct_scope_count=5,
            mean_effort_minutes=120,
            repair_success_ratio=1.0,
            false_positive_ratio=0.0,
        )
        self.assertEqual(5.0, score.total)
        self.assertEqual(
            "promotion_eligible",
            candidate_state(score.total),
        )
    def test_low_score_is_deferred(self) -> None:
        self.assertEqual("deferred", candidate_state(2.99))
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/compilation/test_regression.py <<'EOF'
from __future__ import annotations
import unittest
from l9_debt_intelligence.compilation.emitters import (
    regression_fixtures,
)
from l9_debt_intelligence.compilation.regression import (
    evaluate_fixture,
)
class RegressionTests(unittest.TestCase):
    def candidate(self) -> dict:
        return {
            "candidate_id": "candidate_" + ("a" * 64),
            "recurrence_fingerprint": "b" * 64,
            "match_contract": {
                "event_class": "repair_attempt",
                "recurrence_fingerprint": "b" * 64,
            },
        }
    def test_positive_and_negative_fixtures_pass(self) -> None:
        candidate = self.candidate()
        results = [
            evaluate_fixture(candidate, fixture)
            for fixture in regression_fixtures(candidate)
        ]
        self.assertEqual(
            ["passed", "passed"],
            [result["status"] for result in results],
        )
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/compilation/test_compilation_lifecycle.py <<'EOF'
from __future__ import annotations
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from l9_debt_intelligence.analytics.builder import build_analytics
from l9_debt_intelligence.compilation.builder import (
    build_compilation,
)
from l9_debt_intelligence.compilation.verify import (
    verify_compilation,
)
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
class CompilationLifecycleTests(unittest.TestCase):
    def test_compilation_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ingestion = root / "ingestion"
            snapshots = root / "snapshots"
            analytics = root / "analytics"
            compilations = root / "compilations"
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
            analysis = build_analytics(
                snapshot_path=snapshot.snapshot_path,
                analytics_root=analytics,
            )
            first = build_compilation(
                analysis_path=Path(analysis["analysis_path"]),
                compilation_root=compilations,
            )
            second = build_compilation(
                analysis_path=Path(analysis["analysis_path"]),
                compilation_root=compilations,
            )
            self.assertEqual(
                first["compilation_id"],
                second["compilation_id"],
            )
            self.assertEqual(
                first["deterministic_output_hash"],
                second["deterministic_output_hash"],
            )
            verification = verify_compilation(
                Path(first["compilation_path"])
            )
            self.assertEqual("valid", verification["status"])
if __name__ == "__main__":
    unittest.main()
EOF
cat > tests/architecture/test_compiler_boundary.py <<'EOF'
from __future__ import annotations
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/compilation"
class CompilerBoundaryTests(unittest.TestCase):
    def test_compiler_contains_no_publication_or_mutation(self) -> None:
        prohibited = (
            "git push",
            "create_release",
            "upload_artifact",
            "cosign",
            "sigstore",
            "policy promotion",
            "automatic_promotion",
            "subprocess.run",
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for token in prohibited:
                if token in text:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{token}"
                    )
        self.assertEqual([], violations)
    def test_contract_marks_outputs_as_candidates(self) -> None:
        contract = (
            ROOT / ".l9/compiler-contract.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn("state: candidate_only", contract)
        self.assertIn(
            "automatic_promotion: prohibited",
            contract,
        )
        self.assertIn(
            "defense-pack assembly",
            contract,
        )
if __name__ == "__main__":
    unittest.main()
EOF
cat > .github/workflows/phase-5-compilation.yml <<'EOF'
name: Intelligence Phase 5 compilation
on:
  pull_request:
    paths:
      - ".l9/compiler-contract.yaml"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/compilation/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/compilation/**"
      - "tests/architecture/**"
  push:
    branches:
      - main
    paths:
      - ".l9/compiler-contract.yaml"
      - "schemas/intelligence/**"
      - "src/l9_debt_intelligence/compilation/**"
      - "src/l9_debt_intelligence/cli.py"
      - "tests/compilation/**"
      - "tests/architecture/**"
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: intelligence-phase-5-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  compile:
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
      - name: Run complete contract suite
        run: |
          python -m pytest \
            tests/architecture \
            tests/contracts \
            tests/ingestion \
            tests/snapshots \
            tests/analytics \
            tests/compilation
EOF
cat > docs/architecture/ADRs/ADR-INTEL-015-candidate-only-compilation.md <<'EOF'
# ADR-INTEL-015: Compiled prevention rules remain candidates
- Status: Accepted
- Phase: INTEL-P4
## Decision
INTEL-P4 compiler outputs are candidate artifacts. They cannot independently
enable blocking policy, promote themselves, mutate repositories, or execute
external commands.
Promotion belongs to later signed publication and Core governance.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-016-unknowns-do-not-increase-score.md <<'EOF'
# ADR-INTEL-016: Unknown evidence cannot increase leverage scores
- Status: Accepted
- Phase: INTEL-P4
## Decision
Unknown effort, repair success, and false-positive information contribute no
positive leverage score.
Missing data is never interpreted as successful repair, high effort, or low
false-positive risk.
EOF
cat > docs/architecture/ADRs/ADR-INTEL-017-compiler-requires-regressions.md <<'EOF'
# ADR-INTEL-017: Every compiled candidate requires regression fixtures
- Status: Accepted
- Phase: INTEL-P4
## Decision
Every non-deferred candidate receives positive and negative fixtures.
Compilation fails when any generated fixture fails.
Later compiler adapters may add language-specific fixtures without weakening
this minimum.
EOF
python3 - <<'PY'
from pathlib import Path
path = Path(".l9/architecture.yaml")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "phase: INTEL-P3",
    "phase: INTEL-P4",
    1,
)
old = """phase_4:
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
new = """phase_4:
  name: learning-metrics
  status: implemented
phase_5:
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
if old not in text:
    raise SystemExit("unexpected INTEL-P3 architecture block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
python3 - <<'PY'
from pathlib import Path
path = Path("ROADMAP.md")
text = path.read_text(encoding="utf-8")
old = """## INTEL-P4 — Rule compilation
Not authorized.
"""
new = """## INTEL-P4 — Rule compilation
Implemented:
- deterministic candidate extraction;
- evidence-bounded leverage scoring;
- explicit candidate lifecycle states;
- generated invariant candidates;
- ast-grep candidate output;
- SDK architecture-contract candidate output;
- positive and negative regression fixtures;
- compiler regression results;
- deterministic compiler manifests.
All generated outputs remain non-blocking candidates.
"""
if old not in text:
    raise SystemExit("unexpected ROADMAP INTEL-P4 block")
path.write_text(
    text.replace(old, new),
    encoding="utf-8",
)
PY
cat >> AGENTS.md <<'EOF'
## INTEL-P4 compiler rules
- Compile only from a verified INTEL-P3 analysis run.
- Preserve source snapshot and analysis-run lineage.
- Keep every generated output in candidate state.
- Never let unknown evidence increase a score.
- Never promote or enable blocking policy from this repository.
- Generate positive and negative regression fixtures.
- Fail compilation when regression fixtures fail.
- Sort candidates and artifacts deterministically.
- Keep signing, release publication, and retirement out of this phase.
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
  tests/analytics \
  tests/compilation
workspace="$(mktemp -d)"
trap 'rm -rf "$workspace"' EXIT
ingestion="${workspace}/ingestion"
snapshots="${workspace}/snapshots"
analytics="${workspace}/analytics"
compilations="${workspace}/compilations"
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
print(json.loads(Path(sys.argv[1]).read_text())["snapshot_id"])
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
print(json.loads(Path(sys.argv[1]).read_text())["analysis_path"])
PY
)"
l9-intelligence compile-candidates \
  "$analysis_path" \
  --compilation-root "$compilations" \
  --output "${workspace}/compilation.json"
compilation_path="$(
  python - "${workspace}/compilation.json" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text())["compilation_path"])
PY
)"
l9-intelligence verify-compilation \
  "$compilation_path" \
  --output "${workspace}/verification.json"
python - "${workspace}/verification.json" <<'PY'
import json
import sys
from pathlib import Path
value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)
assert value["status"] == "valid", value
assert value["verified_artifact_count"] >= 4, value
PY
printf '\nINTEL-P4 rule compilation built and validated.\n'
printf 'Snapshot: %s\n' "$snapshot_id"
printf 'Analysis: %s\n' "$analysis_path"
printf 'Compilation: %s\n' "$compilation_path"

Execute:

chmod +x build-phase-5.sh
./build-phase-5.sh

Then commit:

git status --short
git diff --check
git add \
  .l9 \
  .github/workflows/phase-5-compilation.yml \
  schemas/intelligence \
  src/l9_debt_intelligence \
  tests/architecture \
  tests/compilation \
  docs/architecture/ADRs \
  AGENTS.md \
  ROADMAP.md
git commit -m "feat!: implement Intelligence INTEL-P4 rule compilation"

The resulting boundary is:

verified analysis run
        ↓
candidate extraction
        ↓
evidence-bounded scoring
        ├── deferred
        ├── compiled candidate
        └── promotion eligible
        ↓
candidate compilers
        ├── generated invariants
        ├── ast-grep candidates
        ├── SDK contract candidates
        └── regression fixtures
        ↓
verified immutable compiler manifest

promotion_eligible means only that a candidate meets the configured score threshold. It does not authorize publication or blocking enforcement. The next phase is INTEL-P5: signed defense-pack assembly and publication.