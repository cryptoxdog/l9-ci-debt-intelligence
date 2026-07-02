"""Ingest resolver JSONL findings into the corpus staging area."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import typer

app = typer.Typer()

SCHEMA_PATH = Path(__file__).parents[2] / "schemas" / "corpus.schema.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


@app.command()
def ingest(
    findings_jsonl: Path = typer.Argument(..., help="Path to PR_REMEDIATION_FINDINGS.jsonl from resolver"),
    output_dir: Path = typer.Option(Path("outputs/corpus"), help="Staging output directory"),
    validate: bool = typer.Option(True, help="Validate each record against corpus schema"),
) -> None:
    """Read resolver findings JSONL, validate, and write to outputs/corpus/unified_findings.jsonl."""
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = _load_schema() if validate else None

    records: list[dict] = []
    errors: list[str] = []

    for lineno, raw in enumerate(findings_jsonl.read_text().splitlines(), start=1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {lineno}: JSON decode error — {exc}")
            continue

        if schema:
            try:
                jsonschema.validate(instance=record, schema=schema)
            except jsonschema.ValidationError as exc:
                errors.append(f"line {lineno}: schema violation — {exc.message}")
                continue

        records.append(record)

    out_path = output_dir / "unified_findings.jsonl"
    with out_path.open("w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")

    typer.echo(f"Ingested {len(records)} records → {out_path}")
    if errors:
        typer.echo(f"WARN: {len(errors)} records skipped:", err=True)
        for e in errors:
            typer.echo(f"  {e}", err=True)
        if len(errors) == len(records) + len(errors):
            sys.exit(1)


if __name__ == "__main__":
    app()
