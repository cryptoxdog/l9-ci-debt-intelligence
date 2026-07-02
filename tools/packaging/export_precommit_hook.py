"""Export a .pre-commit-config.yaml fragment including the ast-grep pack."""
from __future__ import annotations

from pathlib import Path

import typer
import yaml

app = typer.Typer()


@app.command()
def export(
    output_path: Path = typer.Option(Path("outputs/defense/scaffolds/python-gha/.pre-commit-config.yaml")),
    astgrep_rules_dir: str = typer.Option("outputs/defense/astgrep/rules"),
) -> None:
    config = {
        "repos": [
            {
                "repo": "https://github.com/astral-sh/ruff-pre-commit",
                "rev": "v0.4.10",
                "hooks": [{"id": "ruff", "args": ["--fix"]}, {"id": "ruff-format"}],
            },
            {
                "repo": "https://github.com/pre-commit/pre-commit-hooks",
                "rev": "v4.6.0",
                "hooks": [
                    {"id": "check-yaml"},
                    {"id": "check-json"},
                    {"id": "end-of-file-fixer"},
                    {"id": "trailing-whitespace"},
                ],
            },
            {
                "repo": "local",
                "hooks": [{
                    "id": "ast-grep-ci-debt",
                    "name": "ast-grep CI-debt rules",
                    "language": "system",
                    "entry": f"ast-grep scan --config {astgrep_rules_dir}",
                    "types": ["python", "yaml", "toml"],
                    "pass_filenames": False,
                }],
            },
        ]
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump(config, sort_keys=False, allow_unicode=True))
    typer.echo(f"Pre-commit config → {output_path}")


if __name__ == "__main__":
    app()
