from __future__ import annotations

import unittest

from l9_debt_intelligence.analytics.metrics import (
    effectiveness_rows,
    effort_rows,
)
from l9_debt_intelligence.analytics.models import LearningObservation


class UnknownSemanticsTests(unittest.TestCase):
    def observation(self) -> LearningObservation:
        return LearningObservation(
            record_id="cr_" + ("a" * 64),
            producer_id="producer",
            event_class="gate_outcome",
            producer_contract="contract/v1",
            occurrence_scope="run-1",
            recurrence_fingerprint="b" * 64,
        )

    def test_missing_effort_is_not_zero(self) -> None:
        row = effort_rows([self.observation()])[0]
        self.assertEqual(0, row["known_observation_count"])
        self.assertEqual(1, row["unknown_observation_count"])
        self.assertIsNone(row["total_minutes"])
        self.assertIsNone(row["mean_minutes"])

    def test_missing_outcomes_do_not_produce_ratio(self) -> None:
        row = effectiveness_rows([self.observation()])[0]
        self.assertIsNone(row["false_positive_ratio"])
        self.assertIsNone(row["success_ratio"])
        self.assertEqual(1, row["unknown_count"])
        self.assertEqual(1, row["validation_unknown_count"])


if __name__ == "__main__":
    unittest.main()
