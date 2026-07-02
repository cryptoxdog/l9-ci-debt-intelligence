"""Bundle scaffold directories into dist/scaffolds for distribution."""
from __future__ import annotations

import shutil
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def export(
    scaffolds_dir: Path = typer.Option(Path("outputs/defense/scaffolds")),
    output_dir: Path = typer.Option(Path("dist/scaffolds")),
) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)

    if scaffolds_dir.exists():
        shutil.copytree(scaffolds_dir, output_dir)
        scaffold_names = [d.name for d in output_dir.iterdir() if d.is_dir()]
        typer.echo(f"Scaffolds exported: {scaffold_names} → {output_dir}")
    else:
        typer.echo(f"WARN: no scaffolds found at {scaffolds_dir}")


if __name__ == "__main__":
    app()
