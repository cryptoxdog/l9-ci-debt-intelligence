"""Contract test: resolver-format findings map to corpus-schema-valid records.

Proves the resolver -> intelligence ingest wire is deterministic and that
mapped records survive corpus schema validation (instead of being dropped).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from tools.corpus.map_resolver_findings import map_record

RESOLVER_FIXTURE = Path(__file__).parent / "fixtures" / "resolver_corpus" / "CI_DEBT_FINDINGS.jsonl"
CORPUS_SCHEMA = Path(__file__).parents[1] / "schemas" / "corpus.schema.json"


def load_resolver_findings() -> list[dict]:
    return [json.loads(line) for line in RESOLVER_FIXTURE.read_text().splitlines() if line.strip()]


def map_all() -> list[dict]:
    return [map_record(r, ci_system="github-actions", language="unknown") for r in load_resolver_findings()]


def test_resolver_fixture_loads():
    assert len(load_resolver_findings()) == 3


def test_mapped_records_validate_against_corpus_schema():
    schema = json.loads(CORPUS_SCHEMA.read_text())
    for record in map_all():
        jsonschema.validate(instance=record, schema=schema)


def test_outcome_to_classification_mapping():
    by_id = {r["finding_id"]: r for r in map_all()}
    assert by_id["CI-IMPORT-001-fixture"]["classification"] == "valid_current"
    assert by_id["CI-DEPS-001-fixture"]["classification"] == "valid_current"
    assert by_id["CI-LOG-EXPIRED-fixture"]["classification"] == "unknown"


def test_outcome_to_action_mapping():
    by_id = {r["finding_id"]: r for r in map_all()}
    assert by_id["CI-IMPORT-001-fixture"]["action"] == "patch"
    assert by_id["CI-DEPS-001-fixture"]["action"] == "not_patched"
    assert by_id["CI-LOG-EXPIRED-fixture"]["action"] == "not_patched"


def test_rule_id_from_failure_type():
    by_id = {r["finding_id"]: r for r in map_all()}
    assert by_id["CI-IMPORT-001-fixture"]["rule_id"] == "CI-IMPORT"
    assert by_id["CI-DEPS-001-fixture"]["rule_id"] == "CI-DEPS"


def test_tenant_id_from_repo_owner():
    for record in map_all():
        assert record["tenant_id"] == "Quantum-L9"


def test_source_enum_collision_resolved():
    for record in map_all():
        assert record["source"] == "gha_log"
        assert record["resolver_source"] == "l9-ci-debt-resolver"


def test_provenance_preserved():
    by_id = {r["finding_id"]: r for r in map_all()}
    rec = by_id["CI-IMPORT-001-fixture"]
    assert rec["failure_type"] == "CI-IMPORT"
    assert rec["root_cause"].startswith("PYTHONPATH")
    assert rec["outcome"] == "repaired"
    assert rec["created_at"] == "2026-07-02T12:00:00Z"


def test_mapping_is_deterministic():
    first = map_all()
    second = map_all()
    assert [json.dumps(r, sort_keys=True) for r in first] == [json.dumps(r, sort_keys=True) for r in second]


def test_pr_number_becomes_pr():
    by_id = {r["finding_id"]: r for r in map_all()}
    assert by_id["CI-IMPORT-001-fixture"]["pr"] == 1
    assert by_id["CI-LOG-EXPIRED-fixture"]["pr"] == 3
