"""Normalize unified_findings.jsonl: deduplicate, sort, enrich with topology tags."""
from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

app = typer.Typer()

TOPOLOGY_PATH = Path(__file__).parents[2] / "references" / "topology-taxonomy.md"

# Minimal topology tag map; extended by adapters at runtime
_TOPOLOGY_MAP: dict[str, list[str]] = {
    "CI-IMPORT": ["gha", "python", "env"],
    "CI-DEPS": ["gha", "python", "dependencies"],
    "API-DRIFT": ["python", "schema", "api"],
    "DOCTRINE": ["wire-format", "transport"],
}


def _topology_tags(finding_id: str) -> list[str]:
    prefix = finding_id.split("-")[0] + "-" + finding_id.split("-")[1] if "-" in finding_id else finding_id
    for key, tags in _TOPOLOGY_MAP.items():
        if finding_id.startswith(key):
            return tags
    return ["unknown"]


@app.command()
def normalize(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    output_path: Path = typer.Option(Path("outputs/corpus/unified_findings.jsonl")),
) -> None:
    """Deduplicate, sort by PR then finding_id, enrich with topology tags."""
    records: dict[str, dict] = {}

    for raw in corpus_jsonl.read_text().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        r = json.loads(raw)
        key = f"{r.get('pr')}:{r.get('finding_id')}"
        if key not in records:
            r.setdefault("topology_tags", _topology_tags(r.get("finding_id", "")))
            records[key] = r

    sorted_records = sorted(records.values(), key=lambda r: (r.get("pr", 0), r.get("finding_id", "")))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as fh:
        for r in sorted_records:
            fh.write(json.dumps(r) + "\n")

    typer.echo(f"Normalized {len(sorted_records)} unique records → {output_path}")


if __name__ == "__main__":
    app()
