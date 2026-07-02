#!/usr/bin/env python3
"""Export a .pre-commit-config.yaml bundle from generated ast-grep rules."""
from __future__ import annotations
import sys
from pathlib import Path


def main() -> int:
    rules_dir = Path("outputs/defense/astgrep/rules")
    output_path = Path("outputs/packages/pre-commit-config.yaml")

    rules = sorted(rules_dir.glob("*.yaml")) if rules_dir.exists() else []
    if not rules:
        print("WARN: no ast-grep rules found. Run corpus_to_astgrep.py first.")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "repos:",
        "  - repo: https://github.com/ast-grep/ast-grep",
        "    rev: v0.26.0",
        "    hooks:",
        "      - id: ast-grep",
        "        args: ['--config', 'outputs/defense/astgrep/sgconfig.yml']",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: pre-commit config exported ({len(rules)} rules referenced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
