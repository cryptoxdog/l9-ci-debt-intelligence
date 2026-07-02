"""Generate project scaffolds (pyproject.toml, GHA workflow, AGENTS.md) from adapter profiles."""
from __future__ import annotations

from pathlib import Path

import typer
import yaml

app = typer.Typer()

ADAPTERS_DIR = Path(__file__).parents[2] / "adapters"


@app.command()
def generate(
    adapter: str = typer.Argument("python-uv", help="Adapter name (matches adapters/<name>.yaml)"),
    output_dir: Path = typer.Option(Path("outputs/defense/scaffolds"), help="Output root directory"),
) -> None:
    adapter_path = ADAPTERS_DIR / f"{adapter}.yaml"
    if not adapter_path.exists():
        typer.echo(f"ERROR: adapter not found: {adapter_path}", err=True)
        raise typer.Exit(1)

    spec = yaml.safe_load(adapter_path.read_text())
    scaffold_dir = output_dir / adapter
    scaffold_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in spec.get("scaffold_files", {}).items():
        out = scaffold_dir / filename
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)
        typer.echo(f"  wrote {out}")

    typer.echo(f"Scaffold '{adapter}' → {scaffold_dir}")


if __name__ == "__main__":
    app()
