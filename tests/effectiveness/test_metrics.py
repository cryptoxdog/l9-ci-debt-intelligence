from __future__ import annotations

import unittest

from l9_debt_intelligence.effectiveness.metrics import (
    pack_metrics,
    rule_metrics,
)


def outcome(
    outcome_class: str,
    *,
    latency: int | None = None,
) -> dict:
    return {
        "canonical_rule_id": "l9.debt.rule-1",
        "outcome_class": outcome_class,
        "latency_ms": latency,
    }


class EffectivenessMetricTests(unittest.TestCase):
    def test_unknown_is_not_success(self) -> None:
        rows = rule_metrics(
            [
                outcome("prevented_before_merge"),
                outcome("evaluation_incomplete"),
            ]
        )
        row = rows[0]
        self.assertEqual(1, row["prevention_count"])
        self.assertEqual(1, row["unknown_outcome_count"])
        self.assertEqual(1.0, row["prevention_ratio"])

    def test_false_positive_ratio_uses_classified_diagnostics(self) -> None:
        rows = rule_metrics(
            [
                outcome("diagnostic_accepted"),
                outcome("confirmed_false_positive"),
                outcome("evaluation_incomplete"),
            ]
        )
        self.assertEqual(
            0.5,
            rows[0]["false_positive_ratio"],
        )

    def test_pack_coverage_is_explicit(self) -> None:
        rows = rule_metrics([outcome("diagnostic_accepted")])
        metrics = pack_metrics(
            rows=rows,
            active_rule_count=4,
        )
        self.assertEqual(0.25, metrics["coverage_ratio"])


if __name__ == "__main__":
    unittest.main()
