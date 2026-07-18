from __future__ import annotations

from typing import Any


def evaluate_fixture(
    candidate: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    value = fixture["input"]
    observed = (
        value.get("event_class") == candidate["match_contract"].get("event_class")
        and value.get("recurrence_fingerprint") == candidate["recurrence_fingerprint"]
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
