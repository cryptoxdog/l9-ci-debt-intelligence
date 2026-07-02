"""Build a co-occurrence matrix of finding_ids that appear in the same PR."""
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def build(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    output_path: Path = typer.Option(Path("outputs/offense/cooccurrence_matrix.json")),
) -> None:
    """For each pair of finding_ids that co-occur in the same PR, count frequency."""
    pr_findings: dict[str, list[str]] = defaultdict(list)

    for raw in corpus_jsonl.read_text().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        r = json.loads(raw)
        pr_key = f"{r.get('source_repo', 'default')}:{r.get('pr')}"
        fid = r.get("finding_id", "")
        if fid and r.get("classification") == "valid_current":
            pr_findings[pr_key].append(fid)

    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for findings in pr_findings.values():
        for a, b in combinations(sorted(set(findings)), 2):
            matrix[a][b] += 1
            matrix[b][a] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({k: dict(v) for k, v in matrix.items()}, indent=2))
    typer.echo(f"Co-occurrence matrix ({len(matrix)} nodes) → {output_path}")


if __name__ == "__main__":
    app()
