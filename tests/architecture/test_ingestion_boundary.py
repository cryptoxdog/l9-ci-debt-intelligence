from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/ingestion"


class IngestionBoundaryTests(unittest.TestCase):
    def test_ingestion_contains_no_analytics_or_compiler(self) -> None:
        prohibited = (
            "duckdb",
            "parquet",
            "cooccurrence",
            "candidate_rule",
            "ast_grep",
            "defense_pack",
            "git push",
            "create_pull_request",
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for value in prohibited:
                if value in text:
                    violations.append(f"{path.relative_to(ROOT)}:{value}")
        self.assertEqual([], violations)

    def test_ingestion_contract_is_present(self) -> None:
        contract = ROOT / ".l9/ingestion-contract.yaml"
        self.assertTrue(contract.is_file())
        text = contract.read_text(encoding="utf-8")
        self.assertIn("append-only", text)
        self.assertIn("deterministic normalization", text)
        self.assertIn("quarantine persistence", text)


if __name__ == "__main__":
    unittest.main()
