"""Integration test: fixture corpus → normalize → validate → schema check."""
from __future__ import annotations
import json
from pathlib import Path
import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "fixture_findings.jsonl"
SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "corpus.schema.json"


def load_fixture() -> list[dict]:
    return [json.loads(line) for line in FIXTURE.read_text().splitlines() if line.strip()]


def test_fixture_loads():
    assert len(load_fixture()) == 4


def test_fixture_required_fields():
    required = {"finding_id", "classification", "rule_id", "repo", "tenant_id", "language", "ci_system"}
    for record in load_fixture():
        missing = required - record.keys()
        assert not missing, f"Missing fields in {record['finding_id']}: {missing}"


def test_doctrine_reject_not_patched():
    for r in load_fixture():
        if r["classification"] == "doctrine_reject":
            assert r["action"] == "not_patched", f"doctrine_reject must be not_patched: {r['finding_id']}"


def test_unknown_not_patched():
    for r in load_fixture():
        if r["classification"] == "unknown":
            assert r["action"] == "not_patched", f"unknown must be not_patched: {r['finding_id']}"


def test_schema_exists():
    assert SCHEMA_PATH.exists()


def test_fixture_validates_against_schema():
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text())
    for record in load_fixture():
        jsonschema.validate(instance=record, schema=schema)
