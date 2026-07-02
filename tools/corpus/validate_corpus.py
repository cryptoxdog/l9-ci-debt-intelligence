"""Validate every record in the corpus against corpus.schema.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import typer

app = typer.Typer()

SCHEMA_PATH = Path(__file__).parents[2] / "schemas" / "corpus.schema.json"


@app.command()
def validate(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    strict: bool = typer.Option(False, help="Exit 1 on any validation error"),
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    errors: list[str] = []
    total = 0

    for lineno, raw in enumerate(corpus_jsonl.read_text().splitlines(), start=1):
        raw = raw.strip()
        if not raw:
            continue
        total += 1
        try:
            record = json.loads(raw)
            jsonschema.validate(instance=record, schema=schema)
        except (json.JSONDecodeError, jsonschema.ValidationError) as exc:
            errors.append(f"line {lineno}: {exc}")

    if errors:
        typer.echo(f"FAIL: {len(errors)}/{total} records invalid:", err=True)
        for e in errors:
            typer.echo(f"  {e}", err=True)
        if strict:
            sys.exit(1)
    else:
        typer.echo(f"OK: all {total} records valid against corpus schema")


if __name__ == "__main__":
    app()
