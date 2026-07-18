from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/publication"


class PublicationBoundaryTests(unittest.TestCase):
    def test_publication_cannot_mutate_core_governance(self) -> None:
        prohibited = (
            "rule-modes.yaml",
            "quality-thresholds.yaml",
            "waivers.yaml",
            "git push",
            "merge_pull_request",
            "create_pull_request",
            "blocking = true",
            '"blocking": true',
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for value in prohibited:
                if value.lower() in text:
                    violations.append(f"{path.relative_to(ROOT)}:{value}")
        self.assertEqual([], violations)

    def test_private_keys_are_not_repository_files(self) -> None:
        prohibited_suffixes = {
            ".pem",
            ".key",
            ".p12",
            ".pfx",
        }
        violations = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in prohibited_suffixes
            and ".git" not in path.parts
        ]
        self.assertEqual([], violations)

    def test_publication_contract_has_rollback(self) -> None:
        contract = (ROOT / ".l9/publication-contract.yaml").read_text(encoding="utf-8")
        self.assertIn(
            "previous known-good version is retained",
            contract,
        )
        self.assertIn(
            "Core governance mutation",
            contract,
        )


if __name__ == "__main__":
    unittest.main()
