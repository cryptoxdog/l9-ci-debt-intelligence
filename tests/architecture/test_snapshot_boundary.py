from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/snapshots"


class SnapshotBoundaryTests(unittest.TestCase):
    def test_snapshot_layer_contains_no_learning_or_compilation(self) -> None:
        prohibited = (
            "cooccurrence",
            "recurrence",
            "effort_atlas",
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

    def test_snapshot_contract_declares_immutability(self) -> None:
        contract = (ROOT / ".l9/snapshot-contract.yaml").read_text(encoding="utf-8")
        required = (
            "existing snapshot objects are never overwritten",
            "identical inputs resolve to the same snapshot identity",
            "DuckDB",
            "Parquet",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, contract)


if __name__ == "__main__":
    unittest.main()
