from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence/compilation"


class CompilerBoundaryTests(unittest.TestCase):
    def test_compiler_contains_no_publication_or_mutation(self) -> None:
        prohibited = (
            "git push",
            "create_release",
            "upload_artifact",
            "cosign",
            "sigstore",
            "policy promotion",
            "automatic_promotion",
            "subprocess.run",
        )
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for token in prohibited:
                if token in text:
                    violations.append(f"{path.relative_to(ROOT)}:{token}")
        self.assertEqual([], violations)

    def test_contract_marks_outputs_as_candidates(self) -> None:
        contract = (ROOT / ".l9/compiler-contract.yaml").read_text(encoding="utf-8")
        self.assertIn("state: candidate_only", contract)
        self.assertIn(
            "automatic_promotion: prohibited",
            contract,
        )
        self.assertIn(
            "defense-pack assembly",
            contract,
        )


if __name__ == "__main__":
    unittest.main()
