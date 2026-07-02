#!/usr/bin/env python3
"""Validate all output artifacts against their schemas. Enforces Gates OV + DV."""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed", file=sys.stderr)
    sys.exit(1)

SCHEMA_DIR = Path("schemas")
CHECKS = [
    (Path("outputs/offense/cooccurrence_matrix.json"), SCHEMA_DIR / "cooccurrence.schema.json", "OV"),
    (Path("outputs/offense/effort_atlas.json"), SCHEMA_DIR / "effort_atlas.schema.json", "OV"),
    (Path("outputs/offense/generated_invariants.yaml"), None, "OV"),  # YAML not JSON-schema validated here
]


def validate_json(data_path: Path, schema_path: Path, gate: str) -> bool:
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(data, schema)
        print(f"GATE_{gate} PASS: {data_path.name}")
        return True
    except jsonschema.ValidationError as e:
        print(f"GATE_{gate} FAIL: {data_path.name} — {e.message}")
        return False
    except Exception as e:
        print(f"GATE_{gate} ERROR: {data_path.name} — {e}")
        return False


def main() -> int:
    failures = 0
    for data_path, schema_path, gate in CHECKS:
        if not data_path.exists():
            print(f"GATE_{gate} MISSING: {data_path}")
            failures += 1
            continue
        if schema_path:
            if not validate_json(data_path, schema_path, gate):
                failures += 1
        else:
            if data_path.stat().st_size > 0:
                print(f"GATE_{gate} PASS (non-empty): {data_path.name}")
            else:
                print(f"GATE_{gate} FAIL (empty): {data_path.name}")
                failures += 1

    # Check defense artifacts exist
    defense_checks = [
        Path("outputs/defense/copilot/copilot-instructions.md"),
        Path("outputs/defense/astgrep/sgconfig.yml"),
        Path("outputs/defense/pr-checklists/checklist_library.yaml"),
    ]
    for p in defense_checks:
        if p.exists() and p.stat().st_size > 0:
            print(f"GATE_DV PASS: {p.name}")
        else:
            print(f"GATE_DV MISSING: {p}")
            failures += 1

    print(f"\nValidation complete: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
