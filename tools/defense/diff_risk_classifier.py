#!/usr/bin/env python3
"""Produce a diff risk model mapping file path patterns to risk scores."""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    atlas_path = Path("outputs/offense/effort_atlas.json")
    output_path = Path("outputs/defense/diff_risk_model.json")

    if not corpus_path.exists():
        print("ERROR: corpus not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    # Map file path patterns to rule_id frequency
    path_rule: dict[str, Counter] = defaultdict(Counter)
    for rec in records:
        loc = rec.get("location", "")
        if ":" in loc:
            file_part = loc.split(":")[0]
        else:
            file_part = loc
        if file_part and file_part != "repo-wide":
            rid = rec.get("rule_id") or "unclassified"
            path_rule[file_part][rid] += 1

    # Load effort scores
    effort: dict[str, float] = {}
    if atlas_path.exists():
        atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
        for rule in atlas.get("rules", []):
            score = rule.get("effort_score")
            if isinstance(score, (int, float)):
                effort[rule["rule_id"]] = score

    model = []
    for file_path, rule_counts in path_rule.items():
        risk = sum(effort.get(rid, 1.0) * count for rid, count in rule_counts.items())
        model.append({"path_pattern": file_path, "risk_score": round(risk, 2),
                       "rule_contributions": dict(rule_counts)})
    model.sort(key=lambda x: x["risk_score"], reverse=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "corpus",
        "leverage_score": 4.1,
        "model": model,
    }, indent=2), encoding="utf-8")
    print(f"OK: diff risk model written ({len(model)} file patterns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
