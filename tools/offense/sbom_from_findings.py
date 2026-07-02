"""Derive a minimal CycloneDX SBOM from corpus dependency findings (CI-DEPS class)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def generate(
    corpus_jsonl: Path = typer.Argument(Path("outputs/corpus/unified_findings.jsonl")),
    output_path: Path = typer.Option(Path("outputs/offense/sbom/sbom.cdx.json")),
) -> None:
    """Build a CycloneDX 1.5 SBOM from CI-DEPS findings in the corpus."""
    components: list[dict] = []
    seen: set[str] = set()

    for raw in corpus_jsonl.read_text().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        r = json.loads(raw)
        if not r.get("finding_id", "").startswith("CI-DEPS"):
            continue
        dep = r.get("description", "").split("not in")[0].strip().split()[-1] if "not in" in r.get("description", "") else r.get("finding_id")
        if dep in seen:
            continue
        seen.add(dep)
        components.append({
            "type": "library",
            "bom-ref": str(uuid.uuid4()),
            "name": dep,
            "version": "UNKNOWN",
            "purl": f"pkg:pypi/{dep.lower()}",
            "evidence": {"identity": [{"field": "purl", "confidence": 0.5, "methods": [{"technique": "source-code-analysis"}]}]},
        })

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tools": [{"name": "l9-ci-debt-intelligence/sbom_from_findings", "version": "0.1.0"}],
            "component": {"type": "application", "name": "l9-ci-debt-corpus"},
        },
        "components": components,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sbom, indent=2))
    typer.echo(f"SBOM ({len(components)} components) → {output_path}")


if __name__ == "__main__":
    app()
