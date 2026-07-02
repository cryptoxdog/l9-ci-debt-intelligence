#!/usr/bin/env python3
"""Validate topology coverage >= 80%. Enforces Gate TC."""
from __future__ import annotations
import json
import sys
from pathlib import Path

MIN_COVERAGE = 0.80


def main() -> int:
    summary_path = Path("outputs/corpus/topology_summary.json")

    if not summary_path.exists():
        print("GATE_TC MISSING: topology_summary.json not found. Run normalize_corpus.py first.")
        return 1

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    coverage_pct = data.get("coverage_pct", 0)
    coverage = coverage_pct / 100.0
    warning = data.get("coverage_warning", True)

    if warning or coverage < MIN_COVERAGE:
        print(f"GATE_TC WARN: topology coverage {coverage_pct:.1f}% < {MIN_COVERAGE*100:.0f}% minimum")
        print("Topology counts:", json.dumps(data.get("topology_counts", {})))
        return 0  # warn, do not block per validation-gates.md

    print(f"GATE_TC PASS: topology coverage {coverage_pct:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
