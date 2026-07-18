from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/effectiveness"


class EffectivenessBoundaryTests(unittest.TestCase):
    def test_effectiveness_cannot_activate_or_retire(self) -> None:
        prohibited = (
            "git push",
            "merge_pull_request",
            "rule-modes.yaml",
            "quality-thresholds.yaml",
            "activate_pack",
            "uninstall_pack",
            "delete_release",
            "gh release delete",
            "automatic_rollback",
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for token in prohibited:
                if token.lower() in text:
                    violations.append(f"{path.relative_to(ROOT)}:{token}")
        self.assertEqual([], violations)

    def test_contract_preserves_unknown_semantics(self) -> None:
        contract = (ROOT / ".l9/effectiveness-contract.yaml").read_text(
            encoding="utf-8"
        )
        required = (
            "Incomplete evaluation is not PASS.",
            "Rule not evaluated is not rule success.",
            "automatic rollback",
            "automatic retirement",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, contract)


if __name__ == "__main__":
    unittest.main()
