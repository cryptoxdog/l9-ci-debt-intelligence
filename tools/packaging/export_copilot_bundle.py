"""Bundle copilot-instructions.md + checklist_library.yaml into a dist/copilot-bundle."""
from __future__ import annotations

import shutil
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def export(
    copilot_md: Path = typer.Option(Path("outputs/defense/copilot/copilot-instructions.md")),
    checklist_yaml: Path = typer.Option(Path("outputs/defense/pr-checklists/checklist_library.yaml")),
    output_dir: Path = typer.Option(Path("dist/copilot-bundle")),
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []

    for src in [copilot_md, checklist_yaml]:
        if src.exists():
            shutil.copy(src, output_dir / src.name)
            copied.append(src.name)
        else:
            typer.echo(f"WARN: {src} not found — skipped", err=True)

    typer.echo(f"Copilot bundle ({', '.join(copied)}) → {output_dir}")


if __name__ == "__main__":
    app()
