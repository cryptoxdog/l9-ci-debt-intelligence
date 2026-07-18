from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/analytics"


class AnalyticsBoundaryTests(unittest.TestCase):
    def test_analytics_contains_no_compiler_or_publication(self) -> None:
        prohibited = (
            "candidate_rule",
            "generated_invariant",
            "ast_grep",
            "defense_pack",
            "signature",
            "git push",
            "create_release",
            "upload_artifact",
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for value in prohibited:
                if value in text:
                    violations.append(f"{path.relative_to(ROOT)}:{value}")
        self.assertEqual([], violations)

    def test_contract_preserves_unknowns(self) -> None:
        contract = (ROOT / ".l9/analytics-contract.yaml").read_text(encoding="utf-8")
        self.assertIn(
            "Unknown dimensions remain explicitly unknown.",
            contract,
        )
        self.assertIn(
            "Missing values are never converted to zero.",
            contract,
        )


if __name__ == "__main__":
    unittest.main()
