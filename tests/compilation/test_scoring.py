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
