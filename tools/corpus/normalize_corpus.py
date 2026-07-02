#!/usr/bin/env python3
"""Normalize corpus: fill missing topology, compute topology_summary.json."""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TOPOLOGY_CLASSES = [
    "gha_workflow", "python_deps", "api_drift", "test_isolation",
    "doctrine_violation", "semantic_tolerance", "unclassified"
]

RULE_TO_TOPOLOGY = {
    "CI-IMPORT-001": "gha_workflow",
    "CI-DEPS-001": "python_deps",
    "API-DRIFT-001": "api_drift",
    "CI-DEPS-002": "gha_workflow",
}


def infer_topology(rec: dict) -> str:
    rule_id = rec.get("rule_id")
    if rule_id and rule_id in RULE_TO_TOPOLOGY:
        return RULE_TO_TOPOLOGY[rule_id]
    cls = rec.get("classification", "")
    if cls == "doctrine_reject":
        return "doctrine_violation"
    return "unclassified"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: normalize_corpus.py --corpus <path>", file=sys.stderr)
        return 1

    corpus_path = Path(sys.argv[sys.argv.index("--corpus") + 1]) if "--corpus" in sys.argv else None
    if not corpus_path or not corpus_path.exists():
        print("ERROR: corpus file not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    normalized = []
    for rec in records:
        if not rec.get("topology"):
            rec["topology"] = infer_topology(rec)
        normalized.append(rec)

    # Rewrite corpus
    with corpus_path.open("w", encoding="utf-8") as fh:
        for rec in normalized:
            fh.write(json.dumps(rec) + "\n")

    # Write topology_summary.json
    summary: dict[str, int] = {t: 0 for t in TOPOLOGY_CLASSES}
    for rec in normalized:
        t = rec.get("topology", "unclassified")
        summary[t] = summary.get(t, 0) + 1

    active_with_findings = sum(1 for t in TOPOLOGY_CLASSES if summary.get(t, 0) > 0)
    coverage = active_with_findings / len(TOPOLOGY_CLASSES)

    topology_summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(normalized),
        "topology_counts": summary,
        "coverage_pct": round(coverage * 100, 1),
        "coverage_warning": coverage < 0.80,
    }
    out_path = corpus_path.parent / "topology_summary.json"
    out_path.write_text(json.dumps(topology_summary, indent=2), encoding="utf-8")

    print(f"OK: normalized {len(normalized)} records. Coverage: {coverage:.0%}")
    if coverage < 0.80:
        print(f"WARN: topology coverage {coverage:.0%} < 80%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
