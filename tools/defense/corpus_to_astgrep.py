#!/usr/bin/env python3
"""Generate ast-grep rule YAMLs from corpus findings."""
from __future__ import annotations
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MIN_OCCURRENCES = 2

RULE_PATTERNS = {
    "CI-IMPORT-001": {
        "language": "yaml",
        "pattern": None,
        "regex": r"run:.*python.*-m\s+\w+",
        "message": "GHA job runs Python module but may be missing PYTHONPATH env. Set env: PYTHONPATH: ${{ github.workspace }}",
        "severity": "error",
        "note": "Rule CI-IMPORT-001: missing PYTHONPATH in GHA workflow",
    },
    "CI-DEPS-001": {
        "language": "toml",
        "pattern": None,
        "regex": r"import pydantic",
        "message": "pydantic is imported but may be missing from [project.dependencies] in pyproject.toml.",
        "severity": "warning",
        "note": "Rule CI-DEPS-001: pydantic missing from pyproject.toml dependencies",
    },
    "API-DRIFT-001": {
        "language": "python",
        "pattern": None,
        "regex": r"def load_json_report",
        "message": "Verify tools/review/report.py defines load_json_report(), SuggestedTest, repro_steps, suggested_tests.",
        "severity": "warning",
        "note": "Rule API-DRIFT-001: API drift in report.py",
    },
    "CI-DEPS-002": {
        "language": "yaml",
        "pattern": None,
        "regex": r"Final Decision",
        "message": "Final Decision job detected. Ensure it has an Install deps step before calling Python scripts.",
        "severity": "error",
        "note": "Rule CI-DEPS-002: missing Install deps step in Final Decision job",
    },
}


def write_rule(rule_id: str, spec: dict, rules_dir: Path) -> None:
    severity_map = {"error": "error", "warning": "warning", "info": "hint"}
    rule_content = [
        f"id: {rule_id.lower()}",
        f"language: {spec['language']}",
        "rule:",
    ]
    if spec.get("pattern"):
        rule_content.append(f"  pattern: '{spec['pattern']}'")
    elif spec.get("regex"):
        rule_content.append(f"  regex: '{spec['regex']}'")
    rule_content += [
        f"message: \"{spec['message']}\"",
        f"severity: {severity_map.get(spec['severity'], 'warning')}",
        f"note: \"{spec['note']}\"",
    ]
    out = rules_dir / f"{rule_id.lower()}.yaml"
    out.write_text("\n".join(rule_content) + "\n", encoding="utf-8")


def main() -> int:
    corpus_path = Path("outputs/corpus/unified_findings.jsonl")
    rules_dir = Path("outputs/defense/astgrep/rules")
    sgconfig_path = Path("outputs/defense/astgrep/sgconfig.yml")

    if not corpus_path.exists():
        print("ERROR: corpus not found", file=sys.stderr)
        return 1

    records = [json.loads(l) for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    valid = [r for r in records if r.get("classification") == "valid_current" and r.get("rule_id")]
    counts = Counter(r["rule_id"] for r in valid)

    rules_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for rid, count in counts.most_common():
        if count < MIN_OCCURRENCES:
            continue
        spec = RULE_PATTERNS.get(rid)
        if not spec:
            print(f"WARN: no pattern defined for {rid} — classifying as pattern_unknown, skipping")
            continue
        write_rule(rid, spec, rules_dir)
        written.append(rid)

    sgconfig_lines = [
        f"# sgconfig.yml — generated {datetime.now(timezone.utc).isoformat()}",
        "ruleDirs:",
        "  - rules",
        "rules:",
    ]
    for rid in written:
        sgconfig_lines.append(f"  - id: {rid.lower()}")
    sgconfig_path.write_text("\n".join(sgconfig_lines) + "\n", encoding="utf-8")

    print(f"OK: {len(written)} ast-grep rules written to {rules_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
