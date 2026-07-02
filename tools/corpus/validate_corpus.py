#!/usr/bin/env python3
"""Validate corpus against corpus.schema.json. Enforces Gate CV."""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    if "--corpus" not in sys.argv:
        print("Usage: validate_corpus.py --corpus <jsonl_path> --schema <schema_path>", file=sys.stderr)
        return 1

    corpus_path = Path(sys.argv[sys.argv.index("--corpus") + 1])
    schema_path = Path(sys.argv[sys.argv.index("--schema") + 1]) if "--schema" in sys.argv \
        else Path(__file__).parents[2] / "schemas" / "corpus.schema.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    violations = 0
    for i, rec in enumerate(records):
        errors = list(validator.iter_errors(rec))
        if errors:
            violations += 1
            for e in errors:
                print(f"VIOLATION record[{i}] finding_id={rec.get('finding_id','?')}: {e.message}",
                      file=sys.stderr)

    rate = violations / max(len(records), 1)
    if rate > 0.10:
        print(f"GATE_CV FAIL: violation rate {rate:.1%} exceeds 10% threshold")
        return 1

    valid_current = sum(1 for r in records if r.get("classification") == "valid_current")
    if valid_current == 0:
        print("GATE_CV FAIL: zero valid_current findings in corpus")
        return 1

    print(f"GATE_CV PASS: {len(records)} records, {violations} violations ({rate:.1%}), {valid_current} valid_current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
