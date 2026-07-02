#!/usr/bin/env python3
"""Build PR checklist library keyed by topology class."""
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


CHECKLIST_ITEMS = {
    "universal": [
        "[ ] All GHA jobs that import Python modules have PYTHONPATH set (CI-IMPORT-001)",
        "[ ] All required packages are in [project.dependencies] in pyproject.toml (CI-DEPS-001)",
        "[ ] Every GHA job calling Python has an Install deps step (CI-DEPS-002)",
        "[ ] No PacketEnvelope active transport references in changed files",
        "[ ] Ruff lint passes on all changed Python files",
        "[ ] All changed workflow YAML files are valid YAML",
    ],
    "gha_workflow": [
        "[ ] Verify PYTHONPATH env is set at job level for all Python-running jobs (CI-IMPORT-001)",
        "[ ] Final Decision job has Install deps step (CI-DEPS-002)",
        "[ ] workflow_dispatch inputs are validated",
    ],
    "python_deps": [
        "[ ] pydantic>=2.0 present in [project.dependencies] (CI-DEPS-001)",
        "[ ] No runtime imports that are absent from pyproject.toml",
        "[ ] Dev dependencies separated into [project.optional-dependencies]",
    ],
    "api_drift": [
        "[ ] tools/review/report.py defines SuggestedTest dataclass (API-DRIFT-001)",
        "[ ] tools/review/report.py defines repro_steps and suggested_tests fields",
        "[ ] tools/review/report.py defines load_json_report() function",
    ],
    "doctrine_violation": [
        "[ ] Zero PacketEnvelope active transport references in changed files",
        "[ ] All wire format usage uses TransportPacket",
        "[ ] ADR amendment filed if TransportPacket boundary is modified",
    ],
}


def main() -> int:
    output_path = Path("outputs/defense/pr-checklists/checklist_library.yaml")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    library = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "corpus + doctrine",
        "leverage_score": 4.0,
        "checklists": CHECKLIST_ITEMS,
    }
    output_path.write_text(yaml.dump(library, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    print(f"OK: checklist library written ({len(CHECKLIST_ITEMS)} topology blocks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
