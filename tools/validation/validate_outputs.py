"""Validate all pipeline outputs exist and are non-empty."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

app = typer.Typer()

REQUIRED_OUTPUTS: list[Path] = [
    Path("outputs/corpus/unified_findings.jsonl"),
    Path("outputs/offense/cooccurrence_matrix.json"),
    Path("outputs/offense/effort_atlas.json"),
    Path("outputs/offense/generated_invariants.yaml"),
    Path("outputs/offense/CONTEXT_PRIMERS.md"),
    Path("outputs/defense/copilot/copilot-instructions.md"),
    Path("outputs/defense/pr-checklists/checklist_library.yaml"),
]


@app.command()
def validate(
    strict: bool = typer.Option(False, help="Exit 1 on any missing or empty output"),
) -> None:
    failures: list[str] = []

    for path in REQUIRED_OUTPUTS:
        if not path.exists():
            failures.append(f"MISSING: {path}")
        elif path.stat().st_size == 0:
            failures.append(f"EMPTY:   {path}")

    if failures:
        typer.echo(f"Output validation FAIL ({len(failures)} issues):", err=True)
        for f in failures:
            typer.echo(f"  {f}", err=True)
        if strict:
            sys.exit(1)
    else:
        typer.echo(f"Output validation OK — all {len(REQUIRED_OUTPUTS)} required outputs present")


if __name__ == "__main__":
    app()
