from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

UNKNOWN_OUTCOMES = {
    "rule_not_evaluated",
    "evaluation_incomplete",
    "outcome_unknown",
}
PREVENTION_OUTCOMES = {
    "prevented_before_merge",
    "diagnostic_accepted",
}
DETECTION_OUTCOMES = {
    "detected_in_CI",
    "diagnostic_shown",
}
ESCAPE_OUTCOMES = {
    "escaped_detection",
}
FALSE_POSITIVE_OUTCOMES = {
    "confirmed_false_positive",
}
REPAIR_SUCCESS = {
    "repair_succeeded",
}
REPAIR_FAILURE = {
    "repair_failed",
    "repair_rolled_back",
}


def ratio(
    numerator: int,
    denominator: int,
) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 12)


def p95(values: list[int]) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(
        0,
        math.ceil(len(ordered) * 0.95) - 1,
    )
    return ordered[index]


def rule_metrics(
    outcomes: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for outcome in outcomes:
        grouped[outcome["canonical_rule_id"]].append(outcome)
    rows: list[dict[str, Any]] = []
    for rule_id in sorted(grouped):
        items = grouped[rule_id]
        classes = [item["outcome_class"] for item in items]
        unknown_count = sum(value in UNKNOWN_OUTCOMES for value in classes)
        known_count = len(classes) - unknown_count
        prevention = sum(value in PREVENTION_OUTCOMES for value in classes)
        detection = sum(value in DETECTION_OUTCOMES for value in classes)
        escape = sum(value in ESCAPE_OUTCOMES for value in classes)
        false_positive = sum(value in FALSE_POSITIVE_OUTCOMES for value in classes)
        accepted = classes.count("diagnostic_accepted")
        dismissed = classes.count("diagnostic_dismissed")
        quick_fix_applied = classes.count("quick_fix_applied")
        quick_fix_reverted = classes.count("quick_fix_reverted")
        repair_success = sum(value in REPAIR_SUCCESS for value in classes)
        repair_failure = sum(value in REPAIR_FAILURE for value in classes)
        evaluated_for_prevention = prevention + detection + escape
        diagnostic_classified = accepted + dismissed + false_positive
        quick_fix_classified = quick_fix_applied + quick_fix_reverted
        repair_classified = repair_success + repair_failure
        latencies = [
            item["latency_ms"]
            for item in items
            if isinstance(item.get("latency_ms"), int)
        ]
        rows.append(
            {
                "canonical_rule_id": rule_id,
                "evaluation_count": len(items),
                "known_outcome_count": known_count,
                "unknown_outcome_count": unknown_count,
                "prevention_count": prevention,
                "detection_count": detection,
                "escape_count": escape,
                "false_positive_count": false_positive,
                "accepted_diagnostic_count": accepted,
                "dismissed_diagnostic_count": dismissed,
                "quick_fix_applied_count": quick_fix_applied,
                "quick_fix_reverted_count": quick_fix_reverted,
                "repair_success_count": repair_success,
                "repair_failure_count": repair_failure,
                "prevention_ratio": ratio(
                    prevention,
                    evaluated_for_prevention,
                ),
                "escape_ratio": ratio(
                    escape,
                    evaluated_for_prevention,
                ),
                "false_positive_ratio": ratio(
                    false_positive,
                    diagnostic_classified,
                ),
                "quick_fix_revert_ratio": ratio(
                    quick_fix_reverted,
                    quick_fix_classified,
                ),
                "repair_success_ratio": ratio(
                    repair_success,
                    repair_classified,
                ),
                "p95_latency_ms": p95(latencies),
            }
        )
    return rows


def weighted_ratio(
    rows: list[dict[str, Any]],
    numerator: str,
    denominator_fields: tuple[str, ...],
) -> float | None:
    numerator_total = sum(int(row[numerator]) for row in rows)
    denominator_total = sum(
        sum(int(row[field]) for field in denominator_fields) for row in rows
    )
    return ratio(numerator_total, denominator_total)


def pack_metrics(
    *,
    rows: list[dict[str, Any]],
    active_rule_count: int,
) -> dict[str, Any]:
    evaluation_count = sum(int(row["evaluation_count"]) for row in rows)
    unknown_count = sum(int(row["unknown_outcome_count"]) for row in rows)
    latencies = [
        int(row["p95_latency_ms"])
        for row in rows
        if isinstance(row["p95_latency_ms"], int)
    ]
    return {
        "active_rule_count": active_rule_count,
        "observed_rule_count": len(rows),
        "evaluation_count": evaluation_count,
        "prevention_ratio": weighted_ratio(
            rows,
            "prevention_count",
            (
                "prevention_count",
                "detection_count",
                "escape_count",
            ),
        ),
        "escape_ratio": weighted_ratio(
            rows,
            "escape_count",
            (
                "prevention_count",
                "detection_count",
                "escape_count",
            ),
        ),
        "false_positive_ratio": weighted_ratio(
            rows,
            "false_positive_count",
            (
                "accepted_diagnostic_count",
                "dismissed_diagnostic_count",
                "false_positive_count",
            ),
        ),
        "unknown_ratio": ratio(
            unknown_count,
            evaluation_count,
        ),
        "p95_latency_ms": p95(latencies),
        "coverage_ratio": ratio(
            len(rows),
            active_rule_count,
        ),
    }
