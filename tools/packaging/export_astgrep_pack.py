#!/usr/bin/env python3
"""Package ast-grep rules + sgconfig into a distributable zip."""
from __future__ import annotations
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    astgrep_dir = Path("outputs/defense/astgrep")
    output_path = Path("outputs/packages/astgrep-pack.zip")

    if not astgrep_dir.exists():
        print("ERROR: astgrep output dir not found. Run corpus_to_astgrep.py first.", file=sys.stderr)
        return 1

    files = list(astgrep_dir.rglob("*.yaml")) + list(astgrep_dir.rglob("*.yml"))
    if not files:
        print("WARN: no rule files found in astgrep output dir")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, f.relative_to(astgrep_dir))

    print(f"OK: astgrep-pack.zip created ({len(files)} files, {output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
