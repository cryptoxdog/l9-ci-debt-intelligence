#!/usr/bin/env python3
"""Ingest resolver JSONL findings into the corpus output directory."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_FIELDS = {"pr", "finding_id", "classification", "description"}
VALID_CLASSIFICATIONS = {"valid_current", "unknown", "doctrine_reject", "out_of_scope"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ingest resolver findings corpus")
    p.add_argument("--input", required=True, help="Dir or file containing JSONL findings")
    p.add_argument("--output", required=True, help="Output dir for corpus artifacts")
    return p.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"WARN: skipping malformed line in {path}: {e}", file=sys.stderr)
    return records


def validate_record(rec: dict, idx: int) -> list[str]:
    errors = []
    for f in REQUIRED_FIELDS:
        if f not in rec:
            errors.append(f"record[{idx}] missing required field '{f}'")
    if "classification" in rec and rec["classification"] not in VALID_CLASSIFICATIONS:
        errors.append(f"record[{idx}] invalid classification '{rec['classification']}'")
    return errors


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all JSONL files
    if input_path.is_file():
        jsonl_files = [input_path]
    else:
        jsonl_files = sorted(input_path.rglob("*.jsonl"))

    if not jsonl_files:
        print("ERROR: corpus_missing — no JSONL files found in input path", file=sys.stderr)
        return 1

    all_records: list[dict] = []
    total_violations = 0

    for f in jsonl_files:
        records = load_jsonl(f)
        for i, rec in enumerate(records):
            errors = validate_record(rec, i)
            if errors:
                for e in errors:
                    print(f"SCHEMA_VIOLATION: {e}", file=sys.stderr)
                total_violations += 1
            else:
                all_records.append(rec)

    if not all_records:
        print("ERROR: corpus_missing — zero valid records after ingestion", file=sys.stderr)
        return 1

    violation_rate = total_violations / max(len(all_records) + total_violations, 1)
    if violation_rate > 0.10:
        print(f"ERROR: corpus_corrupt — schema violation rate {violation_rate:.1%} exceeds 10%", file=sys.stderr)
        return 1

    # Deduplicate by finding_id (last write wins)
    deduped: dict[str, dict] = {}
    for rec in all_records:
        deduped[rec["finding_id"]] = rec
    records_out = list(deduped.values())

    # Write unified_findings.jsonl
    out_file = output_dir / "unified_findings.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for rec in records_out:
            fh.write(json.dumps(rec) + "\n")

    # Write repo_index.json
    pr_map: dict[int, dict] = {}
    for rec in records_out:
        pr = rec["pr"]
        if pr not in pr_map:
            pr_map[pr] = {"pr": pr, "finding_count": 0, "valid_current": 0, "unknown": 0,
                          "doctrine_reject": 0, "out_of_scope": 0}
        pr_map[pr]["finding_count"] += 1
        cls = rec.get("classification", "unknown")
        if cls in pr_map[pr]:
            pr_map[pr][cls] += 1

    repo_index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_findings": len(records_out),
        "total_violations_skipped": total_violations,
        "prs": list(pr_map.values()),
    }
    (output_dir / "repo_index.json").write_text(json.dumps(repo_index, indent=2), encoding="utf-8")

    print(f"OK: ingested {len(records_out)} findings from {len(jsonl_files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
