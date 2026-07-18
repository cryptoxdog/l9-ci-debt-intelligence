from __future__ import annotations

import json
import unittest
from pathlib import Path

from l9_debt_intelligence.effectiveness.errors import (
    OutcomeValidationError,
)
from l9_debt_intelligence.effectiveness.validation import (
    OutcomeValidator,
)

ROOT = Path(__file__).resolve().parents[2]


class OutcomeValidationTests(unittest.TestCase):
    def validator(self) -> OutcomeValidator:
        return OutcomeValidator(
            ROOT / "schemas/intelligence/effectiveness-outcome.schema.json"
        )

    def test_valid_lsp_outcome(self) -> None:
        event = json.loads(
            (ROOT / "tests/fixtures/effectiveness/lsp-outcome.json").read_text(
                encoding="utf-8"
            )
        )
        outcome = self.validator().validate(event)
        self.assertEqual("LSP", outcome.surface)
        self.assertEqual(
            "diagnostic_accepted",
            outcome.outcome_class,
        )

    def test_surface_mismatch_is_rejected(self) -> None:
        event = json.loads(
            (ROOT / "tests/fixtures/effectiveness/lsp-outcome.json").read_text(
                encoding="utf-8"
            )
        )
        event["outcome_class"] = "repair_succeeded"
        with self.assertRaises(OutcomeValidationError):
            self.validator().validate(event)


if __name__ == "__main__":
    unittest.main()
