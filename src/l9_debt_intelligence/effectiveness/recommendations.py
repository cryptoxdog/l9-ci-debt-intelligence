from __future__ import annotations

from typing import Any

MINIMUM_RULE_SAMPLE = 20
MINIMUM_PACK_SAMPLE = 100


def rule_recommendation(
    row: dict[str, Any],
) -> dict[str, Any]:
    count = int(row["evaluation_count"])
    reasons: list[str] = []
    state = "retain"
    if count < MINIMUM_RULE_SAMPLE:
        state = "insufficient_evidence"
        reasons.append(f"requires at least {MINIMUM_RULE_SAMPLE} observations")
    else:
        false_positive = row["false_positive_ratio"]
        escape = row["escape_ratio"]
        revert = row["quick_fix_revert_ratio"]
        latency = row["p95_latency_ms"]
        if false_positive is not None and false_positive >= 0.20:
            state = "retirement_recommended"
            reasons.append("false-positive ratio exceeds retirement threshold")
        elif false_positive is not None and false_positive >= 0.10:
            state = "rollback_recommended"
            reasons.append("false-positive ratio exceeds rollback threshold")
        elif escape is not None and escape >= 0.20:
            state = "rollback_recommended"
            reasons.append("escape ratio exceeds rollback threshold")
        elif revert is not None and revert >= 0.25:
            state = "rollback_recommended"
            reasons.append("quick-fix revert ratio exceeds rollback threshold")
        elif (
            (false_positive is not None and false_positive >= 0.05)
            or (escape is not None and escape >= 0.10)
            or (revert is not None and revert >= 0.10)
            or (latency is not None and latency > 200)
        ):
            state = "investigate"
            reasons.append("one or more effectiveness thresholds require review")
        else:
            reasons.append("observed effectiveness remains within thresholds")
    return {
        "scope": "rule",
        "identity": row["canonical_rule_id"],
        "state": state,
        "reasons": reasons,
        "evidence": {
            "evaluation_count": count,
            "false_positive_ratio": row["false_positive_ratio"],
            "escape_ratio": row["escape_ratio"],
            "quick_fix_revert_ratio": row["quick_fix_revert_ratio"],
            "p95_latency_ms": row["p95_latency_ms"],
        },
    }


def pack_recommendation(
    *,
    pack_id: str,
    metrics: dict[str, Any],
    rule_recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluation_count = int(metrics["evaluation_count"])
    reasons: list[str] = []
    if evaluation_count < MINIMUM_PACK_SAMPLE:
        state = "insufficient_evidence"
        reasons.append(f"requires at least {MINIMUM_PACK_SAMPLE} observations")
    else:
        states = {recommendation["state"] for recommendation in rule_recommendations}
        if "retirement_recommended" in states:
            state = "rollback_recommended"
            reasons.append("one or more active rules have retirement recommendations")
        elif "rollback_recommended" in states:
            state = "rollback_recommended"
            reasons.append("one or more active rules exceed rollback thresholds")
        elif "investigate" in states or (
            metrics["unknown_ratio"] is not None and metrics["unknown_ratio"] >= 0.25
        ):
            state = "investigate"
            reasons.append("pack effectiveness or coverage requires investigation")
        else:
            state = "retain"
            reasons.append("pack effectiveness remains within configured thresholds")
    return {
        "scope": "pack",
        "identity": pack_id,
        "state": state,
        "reasons": reasons,
        "evidence": metrics,
    }
