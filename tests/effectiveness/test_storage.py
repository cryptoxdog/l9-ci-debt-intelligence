from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from l9_debt_intelligence.effectiveness.storage import OutcomeStore
from l9_debt_intelligence.effectiveness.validation import (
    OutcomeValidator,
)

ROOT = Path(__file__).resolve().parents[2]


class OutcomeStorageTests(unittest.TestCase):
    def test_duplicate_delivery_is_idempotent(self) -> None:
        validator = OutcomeValidator(
            ROOT / "schemas/intelligence/effectiveness-outcome.schema.json"
        )
        event = json.loads(
            (ROOT / "tests/fixtures/effectiveness/lsp-outcome.json").read_text(
                encoding="utf-8"
            )
        )
        outcome = validator.validate(event)
        with tempfile.TemporaryDirectory() as directory:
            store = OutcomeStore(Path(directory))
            first = store.ingest(outcome)
            second = store.ingest(outcome)
            self.assertEqual("accepted", first["status"])
            self.assertEqual("duplicate", second["status"])
            self.assertEqual(
                first["outcome_id"],
                second["outcome_id"],
            )
            self.assertEqual(1, len(store.load()))


if __name__ == "__main__":
    unittest.main()
