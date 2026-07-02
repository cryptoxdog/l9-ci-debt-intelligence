#!/usr/bin/env python3
"""Generate CONTEXT_PRIMERS.md for injection into resolver AGENTS.md."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    invariants_path = Path("outputs/offense/generated_invariants.yaml")
    output_path = Path("outputs/offense/CONTEXT_PRIMERS.md")

    if not invariants_path.exists():
        print("ERROR: generated_invariants.yaml not found. Run corpus_to_invariants.py first.", file=sys.stderr)
        return 1

    data = yaml.safe_load(invariants_path.read_text(encoding="utf-8"))
    invariants = data.get("invariants", [])
    high_conf = [i for i in invariants if i.get("confidence") in {"high", "medium"}]

    lines = [
        "# CONTEXT PRIMERS",
        f"# Generated: {datetime.now(timezone.utc).isoformat()}",
        f"# Source: generated_invariants.yaml ({len(high_conf)} high/medium confidence invariants)",
        "",
        "## Inject the following blocks into resolver AGENTS.md under KNOWN ROOT CAUSES:",
        "",
    ]
    for inv in high_conf:
        lines += [
            f"### {inv['rule_id']} ({inv['topology']}) — evidence: {inv['evidence_count']}, confidence: {inv['confidence']}",
            f"- Condition: {inv['condition']}",
            f"- Invariant: {inv['invariant_statement']}",
            "",
        ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: CONTEXT_PRIMERS.md written ({len(high_conf)} primers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
