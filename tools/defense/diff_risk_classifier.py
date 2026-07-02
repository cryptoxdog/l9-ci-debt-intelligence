"""Classify a unified diff for CI-debt risk using the corpus invariant set."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import typer
import yaml

app = typer.Typer()

# Simple token-based risk signals; extend via invariants YAML
_RISK_SIGNALS: list[tuple[str, str, str]] = [
    (r"PacketEnvelope", "DOCTRINE", "high"),
    (r"PYTHONPATH", "CI-IMPORT-001", "medium"),
    (r"pydantic", "CI-DEPS-001", "low"),
    (r"class ReviewReport", "API-DRIFT-001", "medium"),
]


@app.command()
def classify(
    diff_file: Path = typer.Argument(..., help="Unified diff file to classify"),
    invariants_yaml: Path = typer.Option(Path("outputs/offense/generated_invariants.yaml")),
    fail_on_high: bool = typer.Option(False, help="Exit 1 if any high-risk signal found"),
) -> None:
    diff_text = diff_file.read_text()
    findings: list[dict] = []

    for pattern, rule_id, severity in _RISK_SIGNALS:
        matches = list(re.finditer(pattern, diff_text))
        if matches:
            findings.append({"rule_id": rule_id, "severity": severity, "match_count": len(matches)})

    if findings:
        typer.echo(f"Risk signals in diff ({len(findings)} found):")
        for f in findings:
            typer.echo(f"  [{f['severity'].upper()}] {f['rule_id']} — {f['match_count']} match(es)")
        if fail_on_high and any(f["severity"] == "high" for f in findings):
            sys.exit(1)
    else:
        typer.echo("No risk signals detected in diff")


if __name__ == "__main__":
    app()
