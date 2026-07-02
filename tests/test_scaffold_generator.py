"""Test scaffold_generator reads scaffold_files from adapters and writes output."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import pytest, yaml

ADAPTERS_DIR = Path(__file__).parents[1] / "adapters"


@pytest.mark.parametrize("adapter_name", ["github-actions", "python-uv", "node-npm", "polyglot-monorepo"])
def test_adapter_has_scaffold_files(adapter_name):
    path = ADAPTERS_DIR / f"{adapter_name}.yaml"
    spec = yaml.safe_load(path.read_text())
    assert "scaffold_files" in spec
    assert len(spec["scaffold_files"]) > 0


@pytest.mark.parametrize("adapter_name", ["github-actions", "python-uv", "node-npm", "polyglot-monorepo"])
def test_adapter_scaffold_files_have_content(adapter_name):
    spec = yaml.safe_load((ADAPTERS_DIR / f"{adapter_name}.yaml").read_text())
    for filename, content in spec["scaffold_files"].items():
        assert content and content.strip(), f"{adapter_name}/{filename} empty"


def test_scaffold_generator_runs(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "tools.defense.scaffold_generator",
         "github-actions", "--output-dir", str(tmp_path)],
        capture_output=True, text=True,
        cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "github-actions" / ".github" / "workflows" / "ci.yml").exists()
