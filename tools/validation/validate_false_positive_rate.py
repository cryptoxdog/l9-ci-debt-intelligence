"""Estimate false-positive rate: findings classified valid_current but not actioned."""
from __future__ import annotations

import json
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def validate(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    warn_threshold: float = typer.Option(0.15, help="Warn if FP rate exceeds this fraction"),
) -> None:
    total = 0
    valid_current = 0
    not_patched = 0

    for raw in corpus_jsonl.read_text().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        r = json.loads(raw)
        total += 1
        if r.get("classification") == "valid_current":
            valid_current += 1
            if r.get("action") == "not_patched":
                not_patched += 1

    fp_rate = not_patched / valid_current if valid_current else 0.0
    status = "WARN" if fp_rate > warn_threshold else "OK"
    typer.echo(f"{status}: false-positive proxy rate = {fp_rate:.1%} ({not_patched}/{valid_current} valid_current not patched)")


if __name__ == "__main__":
    app()
