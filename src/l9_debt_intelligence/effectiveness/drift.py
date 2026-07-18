from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)

METRICS = (
    "prevention_ratio",
    "escape_ratio",
    "false_positive_ratio",
    "unknown_ratio",
    "coverage_ratio",
    "p95_latency_ms",
)


def delta(
    baseline: float | int | None,
    current: float | int | None,
) -> dict[str, float | None]:
    if baseline is None or current is None:
        return {
            "absolute_delta": None,
            "relative_delta": None,
        }
    absolute = float(current) - float(baseline)
    relative = absolute / float(baseline) if float(baseline) != 0 else None
    return {
        "absolute_delta": round(absolute, 12),
        "relative_delta": (round(relative, 12) if relative is not None else None),
    }


def compare_reports(
    *,
    baseline_path: Path,
    current_path: Path,
) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = json.loads(current_path.read_text(encoding="utf-8"))
    compatible = baseline["pack_id"] == current["pack_id"]
    limitations: list[str] = []
    if not compatible:
        limitations.append("pack identities differ; comparison is informational only")
    metric_deltas = {
        metric: delta(
            baseline["pack_metrics"].get(metric),
            current["pack_metrics"].get(metric),
        )
        for metric in METRICS
    }
    if baseline["observation_count"] == 0 or current["observation_count"] == 0:
        state = "insufficient_evidence"
    else:
        false_positive_delta = metric_deltas["false_positive_ratio"]["absolute_delta"]
        escape_delta = metric_deltas["escape_ratio"]["absolute_delta"]
        latency_delta = metric_deltas["p95_latency_ms"]["absolute_delta"]
        prevention_delta = metric_deltas["prevention_ratio"]["absolute_delta"]
        if (
            (false_positive_delta is not None and false_positive_delta >= 0.10)
            or (escape_delta is not None and escape_delta >= 0.15)
            or (latency_delta is not None and latency_delta >= 800)
        ):
            state = "critical_regression"
        elif (
            (false_positive_delta is not None and false_positive_delta >= 0.03)
            or (escape_delta is not None and escape_delta >= 0.05)
            or (latency_delta is not None and latency_delta >= 100)
        ):
            state = "degraded"
        elif prevention_delta is not None and prevention_delta >= 0.05:
            state = "improved"
        else:
            state = "stable"
    identity = {
        "baseline_report_id": baseline["report_id"],
        "current_report_id": current["report_id"],
        "metric_deltas": metric_deltas,
    }
    return {
        "schema_version": "l9.effectiveness-drift/v1",
        "comparison_id": namespaced_document_hash(
            "drift_",
            identity,
        ),
        "baseline_report_id": baseline["report_id"],
        "current_report_id": current["report_id"],
        "pack_identity_compatible": compatible,
        "metric_deltas": metric_deltas,
        "regression_state": state,
        "limitations": limitations,
    }
