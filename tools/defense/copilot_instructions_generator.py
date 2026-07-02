#!/usr/bin/env python3
"""Generate copilot-instructions.md from corpus invariants."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed", file=sys.stderr)
    sys.exit(1)


INSTRUCTION_TEMPLATES = {
    "CI-IMPORT-001": (
        "Every GitHub Actions job that imports project Python modules MUST set "
        "`env: PYTHONPATH: ${{ github.workspace }}` at the job level.",
        "BAD: job with python -m mymodule but no PYTHONPATH env set.",
        "GOOD: env:\n  PYTHONPATH: ${{ github.workspace }}\nsteps:\n  - run: python -m mymodule",
    ),
    "CI-DEPS-001": (
        "pydantic>=2.0 MUST be listed in [project.dependencies] in pyproject.toml.",
        "BAD: import pydantic in source but no pydantic entry in pyproject.toml.",
        "GOOD: [project.dependencies] = [\"pydantic>=2.0\"]",
    ),
    "API-DRIFT-001": (
        "tools/review/report.py MUST define SuggestedTest dataclass, repro_steps and "
        "suggested_tests fields, and a load_json_report() function.",
        "BAD: report.py missing SuggestedTest or load_json_report.",
        "GOOD: @dataclass class SuggestedTest: ... def load_json_report(path): ...",
    ),
    "CI-DEPS-002": (
        "Every GHA job that calls Python scripts MUST include an Install deps step.",
        "BAD: Final Decision job calls python script with no prior pip install step.",
        "GOOD: - name: Install deps\n  run: pip install pyyaml jsonschema",
    ),
}


def main() -> int:
    invariants_path = Path("outputs/offense/generated_invariants.yaml")
    output_path = Path("outputs/defense/copilot/copilot-instructions.md")

    if not invariants_path.exists():
        print("ERROR: generated_invariants.yaml not found. Run corpus_to_invariants.py first.", file=sys.stderr)
        return 1

    data = yaml.safe_load(invariants_path.read_text(encoding="utf-8"))
    invariants = [i for i in data.get("invariants", []) if i.get("confidence") in {"high", "medium"}]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "# GitHub Copilot Instructions",
        f"# Generated: {datetime.now(timezone.utc).isoformat()}",
        f"# Source: l9-ci-debt-intelligence corpus",
        f"# Total instructions: {len(invariants)}",
        "---",
        "",
        "You are helping with a Python/TypeScript project that uses GitHub Actions.",
        "Follow these rules strictly:",
        "",
    ]
    for inv in invariants:
        rid = inv["rule_id"]
        tpl = INSTRUCTION_TEMPLATES.get(rid)
        if tpl:
            instruction, neg, pos = tpl
        else:
            instruction = inv["invariant_statement"]
            neg, pos = None, None
        lines.append(f"## {rid} ({inv['topology']})")
        lines.append(f"{instruction}")
        if neg:
            lines.append(f"\n**Avoid:** {neg}")
        if pos:
            lines.append(f"\n**Do:** {pos}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: copilot-instructions.md written ({len(invariants)} instructions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
