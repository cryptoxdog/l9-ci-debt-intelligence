"""Bundle ast-grep rules into a publishable pack directory."""
from __future__ import annotations

import shutil
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def export(
    rules_dir: Path = typer.Option(Path("outputs/defense/astgrep/rules")),
    sgconfig: Path = typer.Option(Path("outputs/defense/astgrep/sgconfig.yml")),
    output_dir: Path = typer.Option(Path("dist/astgrep-pack")),
) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    if rules_dir.exists():
        shutil.copytree(rules_dir, output_dir / "rules")
    if sgconfig.exists():
        shutil.copy(sgconfig, output_dir / "sgconfig.yml")

    rule_count = len(list((output_dir / "rules").glob("*.yaml"))) if (output_dir / "rules").exists() else 0
    typer.echo(f"ast-grep pack ({rule_count} rules) → {output_dir}")


if __name__ == "__main__":
    app()
