from __future__ import annotations

import unittest

from l9_debt_intelligence.effectiveness.recommendations import (
    rule_recommendation,
)


def row(
    *,
    count: int = 20,
    false_positive: float | None = 0.0,
    escape: float | None = 0.0,
    revert: float | None = 0.0,
    latency: int | None = 50,
) -> dict:
    return {
        "canonical_rule_id": "l9.debt.rule-1",
        "evaluation_count": count,
        "false_positive_ratio": false_positive,
        "escape_ratio": escape,
        "quick_fix_revert_ratio": revert,
        "p95_latency_ms": latency,
    }


class RecommendationTests(unittest.TestCase):
    def test_insufficient_sample_is_not_retirement(self) -> None:
        recommendation = rule_recommendation(
            row(
                count=3,
                false_positive=1.0,
            )
        )
        self.assertEqual(
            "insufficient_evidence",
            recommendation["state"],
        )

    def test_high_false_positive_rate_recommends_retirement(self) -> None:
        recommendation = rule_recommendation(row(false_positive=0.25))
        self.assertEqual(
            "retirement_recommended",
            recommendation["state"],
        )

    def test_moderate_regression_recommends_investigation(self) -> None:
        recommendation = rule_recommendation(row(false_positive=0.06))
        self.assertEqual(
            "investigate",
            recommendation["state"],
        )


if __name__ == "__main__":
    unittest.main()
