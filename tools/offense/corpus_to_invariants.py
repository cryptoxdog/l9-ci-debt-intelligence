"""Derive AGENTS.md-compatible invariants from high-frequency corpus patterns."""
from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

app = typer.Typer()


def _finding_to_invariant(fid: str, entry: dict) -> dict:
    return {
        "id": fid,
        "description": f"Prevent recurrence of {fid} ({entry['effort_class']} effort)",
        "trigger": f"Any PR where {fid} was previously classified valid_current",
        "gate": "pre-commit + CI",
        "occurrences": entry["occurrences"],
        "severity": entry.get("severities", ["unknown"])[0],
    }


@app.command()
def generate(
    effort_atlas: Path = typer.Argument(Path("outputs/offense/effort_atlas.json")),
    output_path: Path = typer.Option(Path("outputs/offense/generated_invariants.yaml")),
    min_occurrences: int = typer.Option(2, help="Minimum occurrences to promote to invariant"),
) -> None:
    atlas = json.loads(effort_atlas.read_text())
    invariants = [
        _finding_to_invariant(fid, entry)
        for fid, entry in atlas.items()
        if entry["occurrences"] >= min_occurrences
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump({"invariants": invariants}, sort_keys=False, allow_unicode=True))
    typer.echo(f"Generated {len(invariants)} invariants → {output_path}")


if __name__ == "__main__":
    app()
