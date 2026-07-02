#!/usr/bin/env python3
"""Build effort atlas: per-rule effort cost from corpus."""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    output_path = Path("outputs/offense/effort_atlas.json")

    if not corpus_path.exists():
        print("ERROR: corpus not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    valid = [r for r in records if r.get("classification") == "valid_current"]

    # Aggregate per rule_id
    rule_data: dict[str, dict] = defaultdict(lambda: {
        "rule_id": None, "topology": None, "occurrence_count": 0,
        "prs": set(), "cycles": [], "doctrine_reject_count": 0
    })

    for rec in records:
        rid = rec.get("rule_id") or "unclassified"
        rule_data[rid]["rule_id"] = rid
        rule_data[rid]["topology"] = rec.get("topology")
        if rec.get("classification") == "valid_current":
            rule_data[rid]["occurrence_count"] += 1
            rule_data[rid]["prs"].add(rec["pr"])
        if rec.get("classification") == "doctrine_reject":
            rule_data[rid]["doctrine_reject_count"] += 1
        if rec.get("cycle"):
            rule_data[rid]["cycles"].append(rec["cycle"])

    atlas_rules = []
    for rid, d in rule_data.items():
        avg_cycles = round(sum(d["cycles"]) / len(d["cycles"]), 2) if d["cycles"] else "Unknown"
        effort_score = (
            d["occurrence_count"] * avg_cycles
            if isinstance(avg_cycles, (int, float)) else "Unknown"
        )
        atlas_rules.append({
            "rule_id": rid,
            "topology": d["topology"],
            "occurrence_count": d["occurrence_count"],
            "avg_cycles_to_fix": avg_cycles,
            "avg_gate_failures": "Unknown",
            "prs_affected": len(d["prs"]),
            "effort_score": effort_score,
            "doctrine_reject_count": d["doctrine_reject_count"],
        })

    atlas_rules.sort(key=lambda x: (x["effort_score"] if isinstance(x["effort_score"], (int, float)) else -1), reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "corpus",
        "corpus_size": len(valid),
        "leverage_score": 4.4,
        "rules": atlas_rules,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"OK: effort atlas written ({len(atlas_rules)} rule_ids)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
