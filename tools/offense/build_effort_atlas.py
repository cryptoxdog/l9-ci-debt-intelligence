"""Build an effort atlas: per finding_id, count occurrences and estimate remediation effort."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import typer

app = typer.Typer()

# Effort heuristic: number of files typically touched per finding class
_EFFORT_HEURISTIC: dict[str, str] = {
    "CI-IMPORT": "single-job-env-var",
    "CI-DEPS": "pyproject-or-workflow-step",
    "API-DRIFT": "single-module-extend",
    "DOCTRINE": "multi-file-rewrite",
}


@app.command()
def build(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    output_path: Path = typer.Option(Path("outputs/offense/effort_atlas.json")),
) -> None:
    counter: Counter[str] = Counter()
    severity_map: dict[str, list[str]] = {}
    pr_map: dict[str, set[int]] = {}

    for raw in corpus_jsonl.read_text().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        r = json.loads(raw)
        fid = r.get("finding_id", "")
        if not fid:
            continue
        counter[fid] += 1
        severity_map.setdefault(fid, []).append(r.get("severity", "unknown"))
        pr_map.setdefault(fid, set()).add(r.get("pr", 0))

    atlas = {}
    for fid, count in counter.most_common():
        prefix = "-".join(fid.split("-")[:2])
        atlas[fid] = {
            "occurrences": count,
            "pr_count": len(pr_map.get(fid, set())),
            "severities": list(set(severity_map.get(fid, []))),
            "effort_class": _EFFORT_HEURISTIC.get(prefix, "unknown"),
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(atlas, indent=2))
    typer.echo(f"Effort atlas ({len(atlas)} findings) → {output_path}")


if __name__ == "__main__":
    app()
