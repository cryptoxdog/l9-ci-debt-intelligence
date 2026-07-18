from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ContractInventoryTests(unittest.TestCase):
    def test_phase_1_contracts_exist(self) -> None:
        expected = [
            ".l9/architecture.yaml",
            ".l9/ownership.yaml",
            ".l9/sdk-schema-registry.json",
            ".l9/producer-compatibility.json",
            "schemas/intelligence/corpus-event.schema.json",
            "schemas/intelligence/corpus-record.schema.json",
            "schemas/intelligence/corpus-correction.schema.json",
            "schemas/intelligence/corpus-retraction.schema.json",
            "schemas/intelligence/validation-result.schema.json",
        ]
        for relative in expected:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
