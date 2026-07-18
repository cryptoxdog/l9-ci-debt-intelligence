from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/l9_debt_intelligence"
PROHIBITED_TEXT = (
    "git push",
    "git commit",
    "create_pull_request",
    "merge_pull_request",
    "checkout -b",
    'subprocess.run(["git"',
    "import semgrep",
    "from semgrep",
    "import l9_ci._",
    "from l9_ci._",
)
PROHIBITED_PATH_PARTS = {
    "repair",
    "mutation",
    "branch",
    "scanner_parser",
    "repository_parser",
}


class IntelligenceBoundaryTests(unittest.TestCase):
    def test_authoritative_package_contains_no_mutation_behavior(self) -> None:
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for prohibited in PROHIBITED_TEXT:
                if prohibited.lower() in text:
                    violations.append(f"{path.relative_to(ROOT)}:{prohibited}")
        self.assertEqual([], violations)

    def test_authoritative_package_has_no_prohibited_modules(self) -> None:
        violations = [
            path.relative_to(ROOT).as_posix()
            for path in SOURCE.rglob("*")
            if any(part.lower() in PROHIBITED_PATH_PARTS for part in path.parts)
        ]
        self.assertEqual([], violations)

    def test_authoritative_package_does_not_import_legacy_tools(self) -> None:
        violations: list[str] = []
        for path in SOURCE.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "from tools" in text or "import tools" in text:
                violations.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
