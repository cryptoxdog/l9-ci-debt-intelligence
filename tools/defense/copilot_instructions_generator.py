"""Generate .github/copilot-instructions.md from corpus invariants and effort atlas."""
from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

app = typer.Typer()


@app.command()
def generate(
    invariants_yaml: Path = typer.Option(Path("outputs/offense/generated_invariants.yaml")),
    effort_atlas: Path = typer.Option(Path("outputs/offense/effort_atlas.json")),
    output_path: Path = typer.Option(Path("outputs/defense/copilot/copilot-instructions.md")),
) -> None:
    data = yaml.safe_load(invariants_yaml.read_text())
    atlas = json.loads(effort_atlas.read_text()) if effort_atlas.exists() else {}
    invariants = data.get("invariants", [])

    lines = [
        "# Copilot Instructions — L9 CI-Debt Prevention",
        "",
        "_Auto-generated. Do not edit manually. Re-run `copilot_instructions_generator.py` to update._",
        "",
        "## Hard Rules (violations block the PR)",
        "",
    ]

    for inv in invariants:
        atlas_entry = atlas.get(inv["id"], {})
        effort = atlas_entry.get("effort_class", inv.get("effort_class", "unknown"))
        lines.append(f"- **{inv['id']}**: {inv['description']}")
        lines.append(f"  Effort class: `{effort}` | Gate: {inv['gate']}")
        lines.append("")

    lines += [
        "## Workflow Contract",
        "",
        "- Every GHA job that runs Python must set `env: PYTHONPATH: ${{ github.workspace }}` (CI-IMPORT-001)",
        "- Every dependency used at runtime must appear in `pyproject.toml [project.dependencies]` (CI-DEPS-001)",
        "- Final Decision / aggregate jobs must include an `Install deps` step (CI-DEPS-002)",
        "- Do not use `PacketEnvelope` as an active transport type — use `TransportPacket` only (DOCTRINE)",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    typer.echo(f"Copilot instructions ({len(invariants)} rules) → {output_path}")


if __name__ == "__main__":
    app()
