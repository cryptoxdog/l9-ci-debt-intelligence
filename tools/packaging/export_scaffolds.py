#!/usr/bin/env python3
"""Package scaffold directories into individual zips for distribution."""
from __future__ import annotations
import sys
import zipfile
from pathlib import Path


def main() -> int:
    scaffolds_dir = Path("outputs/defense/scaffolds")
    packages_dir = Path("outputs/packages/scaffolds")

    if not scaffolds_dir.exists():
        print("ERROR: scaffolds dir not found. Run scaffold_generator.py first.", file=sys.stderr)
        return 1

    packages_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    for scaffold in sorted(scaffolds_dir.iterdir()):
        if not scaffold.is_dir():
            continue
        zip_path = packages_dir / f"{scaffold.name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(scaffold.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(scaffold))
        exported.append(scaffold.name)
        print(f"OK: scaffold '{scaffold.name}' packaged -> {zip_path}")

    if not exported:
        print("WARN: no scaffold directories found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
