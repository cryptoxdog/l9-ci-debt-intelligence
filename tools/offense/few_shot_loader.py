#!/usr/bin/env python3
"""Select top-5 resolved findings as few-shot examples for agent context."""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    atlas_path = Path("outputs/offense/effort_atlas.json")
    output_path = Path("outputs/offense/few_shot_examples.yaml")

    if not corpus_path.exists():
        print("ERROR: corpus not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    resolved = [r for r in records if r.get("action") == "patch" and r.get("resolved") is True
                and r.get("classification") == "valid_current"]

    # Sort by effort_score if atlas available
    effort_order: dict[str, float] = {}
    if atlas_path.exists():
        atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
        for rule in atlas.get("rules", []):
            score = rule.get("effort_score")
            if isinstance(score, (int, float)):
                effort_order[rule["rule_id"]] = score

    resolved.sort(key=lambda r: effort_order.get(r.get("rule_id", ""), 0), reverse=True)
    examples = resolved[:5]

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "corpus",
        "examples": [
            {
                "finding_id": ex["finding_id"],
                "rule_id": ex.get("rule_id"),
                "description": ex["description"],
                "commit_sha": ex.get("commit_sha"),
                "pr": ex["pr"],
                "cycle": ex.get("cycle"),
            }
            for ex in examples
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump(out, default_flow_style=False), encoding="utf-8")
    print(f"OK: {len(examples)} few-shot examples written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
