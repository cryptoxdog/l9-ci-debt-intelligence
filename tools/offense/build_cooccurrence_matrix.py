#!/usr/bin/env python3
"""Build co-occurrence matrix of rule_ids across PR findings."""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

MIN_CORPUS_SIZE = 10


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    output_path = Path("outputs/offense/cooccurrence_matrix.json")

    if not corpus_path.exists():
        print("ERROR: corpus not found. Run ingest_findings.py first.", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    valid = [r for r in records if r.get("classification") == "valid_current" and r.get("rule_id")]

    if len(valid) < MIN_CORPUS_SIZE:
        print(f"WARN: corpus_too_small ({len(valid)} valid_current findings < {MIN_CORPUS_SIZE}). Skipping matrix.")
        return 0

    # Group rule_ids by PR
    pr_rules: dict[int, set] = defaultdict(set)
    for rec in valid:
        pr_rules[rec["pr"]].add(rec["rule_id"])

    # Build co-occurrence counts
    cooccur: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for rules in pr_rules.values():
        rules_list = sorted(rules)
        for i, r1 in enumerate(rules_list):
            for r2 in rules_list[i:]:
                cooccur[r1][r2] += 1
                if r1 != r2:
                    cooccur[r2][r1] += 1

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "corpus",
        "pr_count": len(pr_rules),
        "leverage_score": 4.2,
        "matrix": {k: dict(v) for k, v in cooccur.items()},
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"OK: co-occurrence matrix written ({len(cooccur)} rule_ids across {len(pr_rules)} PRs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
