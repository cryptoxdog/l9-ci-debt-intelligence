#!/usr/bin/env python3
"""Generate corpus-derived invariants for resolver AGENTS.md injection."""
from __future__ import annotations
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MIN_EVIDENCE = 2


def confidence(count: int) -> str:
    if count >= 5:
        return "high"
    if count >= 3:
        return "medium"
    if count >= MIN_EVIDENCE:
        return "low"
    return "Unknown"


INVARIANT_TEMPLATES = {
    "CI-IMPORT-001": {
        "condition": "A GHA workflow job runs Python but does not set PYTHONPATH",
        "invariant_statement": "Every GHA job that imports project Python modules MUST set env: PYTHONPATH: ${{ github.workspace }}",
    },
    "CI-DEPS-001": {
        "condition": "pydantic is imported in project code but absent from pyproject.toml [project.dependencies]",
        "invariant_statement": "pydantic>=2.0 MUST appear in [project.dependencies] in pyproject.toml for any repo that uses pydantic",
    },
    "API-DRIFT-001": {
        "condition": "tools/review/report.py is missing SuggestedTest dataclass or required fields",
        "invariant_statement": "tools/review/report.py MUST define SuggestedTest, repro_steps, suggested_tests, and load_json_report()",
    },
    "CI-DEPS-002": {
        "condition": "The Final Decision GHA job has no Install deps step",
        "invariant_statement": "Every GHA job that calls Python scripts MUST include an Install deps step with pip install for all required packages",
    },
}


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    output_path = Path("outputs/offense/generated_invariants.yaml")

    if not corpus_path.exists():
        print("ERROR: corpus not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    valid = [r for r in records if r.get("classification") == "valid_current" and r.get("rule_id")]

    counts = Counter(r["rule_id"] for r in valid)

    invariants = []
    for rid, count in counts.most_common():
        if count < MIN_EVIDENCE:
            continue
        tpl = INVARIANT_TEMPLATES.get(rid, {
            "condition": f"rule_id {rid} appears in corpus",
            "invariant_statement": f"Pattern {rid} MUST be prevented per corpus evidence",
        })
        topology = next((r.get("topology") for r in valid if r["rule_id"] == rid), None)
        invariants.append({
            "rule_id": rid,
            "topology": topology,
            "condition": tpl["condition"],
            "invariant_statement": tpl["invariant_statement"],
            "evidence_count": count,
            "confidence": confidence(count),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Write as YAML-ish (hand-formatted for human readability)
    lines = [
        f"# Generated invariants — l9-ci-debt-intelligence",
        f"# generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"# source: corpus",
        f"# leverage_score: 4.6",
        f"# total_invariants: {len(invariants)}",
        "",
        "invariants:",
    ]
    for inv in invariants:
        lines += [
            f"  - rule_id: {inv['rule_id']}",
            f"    topology: {inv['topology']}",
            f"    condition: \"{inv['condition']}\"",
            f"    invariant_statement: \"{inv['invariant_statement']}\"",
            f"    evidence_count: {inv['evidence_count']}",
            f"    confidence: {inv['confidence']}",
        ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: {len(invariants)} invariants written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
