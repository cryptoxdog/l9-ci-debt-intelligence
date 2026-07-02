"""Verify that all topology tags in the corpus have at least one defense artifact."""
from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

app = typer.Typer()


@app.command()
def validate(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    checklist_yaml: Path = typer.Option(Path("outputs/defense/pr-checklists/checklist_library.yaml")),
) -> None:
    corpus_tags: set[str] = set()
    for raw in corpus_jsonl.read_text().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        r = json.loads(raw)
        for tag in r.get("topology_tags", []):
            corpus_tags.add(tag)

    checklist_tags: set[str] = set()
    if checklist_yaml.exists():
        checklists = yaml.safe_load(checklist_yaml.read_text()) or {}
        checklist_tags = set(checklists.keys())

    uncovered = corpus_tags - checklist_tags
    if uncovered:
        typer.echo(f"WARN: {len(uncovered)} topology tags have no checklist coverage: {sorted(uncovered)}")
    else:
        typer.echo(f"OK: all {len(corpus_tags)} corpus topology tags have checklist coverage")


if __name__ == "__main__":
    app()
