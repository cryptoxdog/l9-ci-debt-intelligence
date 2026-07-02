#!/usr/bin/env python3
"""Package Copilot instructions + checklist library into a distributable bundle."""
from __future__ import annotations
import sys
import zipfile
from pathlib import Path


def main() -> int:
    copilot_file = Path("outputs/defense/copilot/copilot-instructions.md")
    checklist_file = Path("outputs/defense/pr-checklists/checklist_library.yaml")
    output_path = Path("outputs/packages/copilot-bundle.zip")

    if not copilot_file.exists():
        print("ERROR: copilot-instructions.md not found. Run copilot_instructions_generator.py first.", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(copilot_file, "copilot-instructions.md")
        if checklist_file.exists():
            zf.write(checklist_file, "checklist_library.yaml")

    print(f"OK: copilot-bundle.zip created ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
