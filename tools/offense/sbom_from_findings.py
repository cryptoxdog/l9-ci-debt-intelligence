#!/usr/bin/env python3
"""Generate CycloneDX 1.4 SBOM from corpus findings."""
from __future__ import annotations
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import uuid


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    output_path = Path("outputs/offense/sbom/sbom.cdx.json")

    if not corpus_path.exists():
        print("ERROR: corpus not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    rule_counts: Counter = Counter(r.get("rule_id") or "unclassified" for r in records
                                   if r.get("classification") == "valid_current")
    reject_counts: Counter = Counter(r.get("rule_id") or "unclassified" for r in records
                                     if r.get("classification") == "doctrine_reject")

    components = []
    for rid, count in rule_counts.most_common():
        risk = "elevated" if reject_counts.get(rid, 0) > 0 else "standard"
        components.append({
            "type": "library",
            "name": rid,
            "version": "corpus-derived",
            "properties": [
                {"name": "occurrence_count", "value": str(count)},
                {"name": "doctrine_reject_count", "value": str(reject_counts.get(rid, 0))},
                {"name": "risk", "value": risk},
            ],
        })

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {"type": "application", "name": "l9-ci-debt-intelligence"},
        },
        "components": components,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sbom, indent=2), encoding="utf-8")
    print(f"OK: SBOM written ({len(components)} components, {sum(1 for c in components if any(p['value']=='elevated' for p in c['properties']))} elevated risk)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
