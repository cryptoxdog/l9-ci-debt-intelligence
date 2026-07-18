from __future__ import annotations

import unittest

from l9_debt_intelligence.analytics.metrics import (
    cooccurrence_rows,
    effectiveness_rows,
    effort_rows,
    recurrence_rows,
)
from l9_debt_intelligence.analytics.models import LearningObservation


def observation(
    record: str,
    scope: str,
    fingerprint: str,
    *,
    effort: int | None = None,
    validation: str | None = None,
    disposition: str | None = None,
    rule: str | None = "rule-1",
) -> LearningObservation:
    return LearningObservation(
        record_id="cr_" + record * 64,
        producer_id="producer",
        event_class="repair_attempt",
        producer_contract="contract/v1",
        occurrence_scope=scope,
        recurrence_fingerprint=fingerprint * 64,
        canonical_rule_id=rule,
        remediation_class="configuration",
        effort_minutes=effort,
        validation_outcome=validation,
        false_positive_disposition=disposition,
    )


class MetricTests(unittest.TestCase):
    def test_recurrence_counts_distinct_scopes(self) -> None:
        rows = recurrence_rows(
            [
                observation("a", "run-1", "1"),
                observation("b", "run-1", "1"),
                observation("c", "run-2", "1"),
            ]
        )
        self.assertEqual(1, len(rows))
        self.assertEqual(3, rows[0]["occurrence_count"])
        self.assertEqual(2, rows[0]["distinct_scope_count"])

    def test_cooccurrence_counts_once_per_scope(self) -> None:
        rows = cooccurrence_rows(
            [
                observation("a", "run-1", "1"),
                observation("b", "run-1", "2"),
                observation("c", "run-2", "1"),
                observation("d", "run-2", "2"),
            ]
        )
        self.assertEqual(1, len(rows))
        self.assertEqual(2, rows[0]["shared_scope_count"])
        self.assertEqual(1.0, rows[0]["jaccard_ratio"])

    def test_missing_effort_remains_unknown(self) -> None:
        rows = effort_rows(
            [
                observation("a", "run-1", "1", effort=10),
                observation("b", "run-2", "1", effort=None),
            ]
        )
        self.assertEqual(1, rows[0]["known_observation_count"])
        self.assertEqual(1, rows[0]["unknown_observation_count"])
        self.assertEqual(10, rows[0]["total_minutes"])

    def test_effectiveness_ratios_use_known_values(self) -> None:
        rows = effectiveness_rows(
            [
                observation(
                    "a",
                    "run-1",
                    "1",
                    validation="passed",
                    disposition="confirmed_true_positive",
                ),
                observation(
                    "b",
                    "run-2",
                    "1",
                    validation="failed",
                    disposition="confirmed_false_positive",
                ),
                observation(
                    "c",
                    "run-3",
                    "1",
                ),
            ]
        )
        self.assertEqual(0.5, rows[0]["success_ratio"])
        self.assertEqual(0.5, rows[0]["false_positive_ratio"])
        self.assertEqual(1, rows[0]["validation_unknown_count"])


if __name__ == "__main__":
    unittest.main()
