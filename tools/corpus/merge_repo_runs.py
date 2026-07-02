#!/usr/bin/env python3
"""Merge multiple resolver corpus runs into a single unified_findings.jsonl."""
from __future__ import annotations
import json
import sys
from pathlib import Path


def main() -> int:
    if "--inputs" not in sys.argv or "--output" not in sys.argv:
        print("Usage: merge_repo_runs.py --inputs <dir1> [dir2 ...] --output <file>", file=sys.stderr)
        return 1

    idx_inputs = sys.argv.index("--inputs") + 1
    idx_output = sys.argv.index("--output")
    input_dirs = sys.argv[idx_inputs:idx_output]
    output_file = Path(sys.argv[idx_output + 1])

    merged: dict[str, dict] = {}
    for d in input_dirs:
        for f in sorted(Path(d).rglob("unified_findings.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                fid = rec.get("finding_id")
                if fid:
                    merged[fid] = rec

    if not merged:
        print("ERROR: no findings found across input directories", file=sys.stderr)
        return 1

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as fh:
        for rec in merged.values():
            fh.write(json.dumps(rec) + "\n")

    print(f"OK: merged {len(merged)} unique findings into {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
