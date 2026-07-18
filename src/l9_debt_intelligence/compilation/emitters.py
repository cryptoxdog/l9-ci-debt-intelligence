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
            "warning" if candidate["state"] == "promotion_eligible" else "info"
        ),
        "evidence": {
            "source_snapshot_id": candidate["source_snapshot_id"],
            "analysis_run_id": candidate["analysis_run_id"],
            "recurrence_fingerprint": candidate["recurrence_fingerprint"],
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
            "regex": ("L9_CANDIDATE_" + candidate["recurrence_fingerprint"][:16]),
        },
        "metadata": {
            "state": "candidate",
            "blocking": False,
            "automatic_fix": False,
            "score": candidate["score"],
            "source_snapshot_id": candidate["source_snapshot_id"],
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
            "source_snapshot_id": candidate["source_snapshot_id"],
            "analysis_run_id": candidate["analysis_run_id"],
            "recurrence_fingerprint": candidate["recurrence_fingerprint"],
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
                "event_class": candidate["match_contract"]["event_class"],
                "recurrence_fingerprint": candidate["recurrence_fingerprint"],
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
