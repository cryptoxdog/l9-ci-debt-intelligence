"""Build a per-topology PR checklist library from corpus invariants."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import typer
import yaml

app = typer.Typer()


@app.command()
def build(
    invariants_yaml: Path = typer.Option(Path("outputs/offense/generated_invariants.yaml")),
    topology_summary: Path = typer.Option(Path("outputs/corpus/topology_summary.json")),
    output_path: Path = typer.Option(Path("outputs/defense/pr-checklists/checklist_library.yaml")),
) -> None:
    data = yaml.safe_load(invariants_yaml.read_text()) if invariants_yaml.exists() else {"invariants": []}
    invariants = data.get("invariants", [])

    checklists: dict[str, list[str]] = defaultdict(list)
    for inv in invariants:
        for tag in inv.get("topology_tags", ["general"]):
            checklists[tag].append(f"- [ ] {inv['id']}: {inv['description']}")

    checklists.setdefault("general", []).insert(0, "- [ ] All 4 local gates (compileall, ruff, pytest, yaml) pass")
    checklists["general"].append("- [ ] No PacketEnvelope in active transport paths")
    checklists["general"].append("- [ ] Tenant isolation test included if data-access layer touched")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump(dict(checklists), sort_keys=True, allow_unicode=True))
    typer.echo(f"Checklist library ({len(checklists)} topologies) → {output_path}")


if __name__ == "__main__":
    app()
