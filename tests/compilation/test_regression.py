from __future__ import annotations

import unittest

from l9_debt_intelligence.compilation.emitters import (
    regression_fixtures,
)
from l9_debt_intelligence.compilation.regression import (
    evaluate_fixture,
)


class RegressionTests(unittest.TestCase):
    def candidate(self) -> dict:
        return {
            "candidate_id": "candidate_" + ("a" * 64),
            "recurrence_fingerprint": "b" * 64,
            "match_contract": {
                "event_class": "repair_attempt",
                "recurrence_fingerprint": "b" * 64,
            },
        }

    def test_positive_and_negative_fixtures_pass(self) -> None:
        candidate = self.candidate()
        results = [
            evaluate_fixture(candidate, fixture)
            for fixture in regression_fixtures(candidate)
        ]
        self.assertEqual(
            ["passed", "passed"],
            [result["status"] for result in results],
        )


if __name__ == "__main__":
    unittest.main()
