"""Merge findings JSONL files from multiple resolver runs / repos into one corpus."""
from __future__ import annotations

import json
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def merge(
    inputs: list[Path] = typer.Argument(..., help="Two or more findings JSONL files to merge"),
    output_path: Path = typer.Option(Path("outputs/corpus/unified_findings.jsonl")),
    deduplicate: bool = typer.Option(True),
) -> None:
    """Concatenate multiple findings JSONL files, optionally deduplicating by (repo, pr, finding_id)."""
    seen: set[str] = set()
    merged: list[dict] = []

    for path in inputs:
        repo_tag = path.stem
        for raw in path.read_text().splitlines():
            raw = raw.strip()
            if not raw:
                continue
            r = json.loads(raw)
            r.setdefault("source_repo", repo_tag)
            key = f"{r.get('source_repo')}:{r.get('pr')}:{r.get('finding_id')}"
            if deduplicate and key in seen:
                continue
            seen.add(key)
            merged.append(r)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as fh:
        for r in merged:
            fh.write(json.dumps(r) + "\n")

    typer.echo(f"Merged {len(merged)} records from {len(inputs)} files → {output_path}")


if __name__ == "__main__":
    app()
