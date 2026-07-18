from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from l9_debt_intelligence.publication.archive import (
    build_deterministic_archive,
)
from l9_debt_intelligence.snapshots.hashing import sha256_file


class ArchiveTests(unittest.TestCase):
    def test_archive_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "a.json").write_text(
                '{"a":1}\\n',
                encoding="utf-8",
            )
            (source / "b.json").write_text(
                '{"b":2}\\n',
                encoding="utf-8",
            )
            first = root / "first.tar.gz"
            second = root / "second.tar.gz"
            build_deterministic_archive(
                source_root=source,
                members=[
                    Path("b.json"),
                    Path("a.json"),
                ],
                destination=first,
            )
            build_deterministic_archive(
                source_root=source,
                members=[
                    Path("a.json"),
                    Path("b.json"),
                ],
                destination=second,
            )
            self.assertEqual(
                sha256_file(first),
                sha256_file(second),
            )


if __name__ == "__main__":
    unittest.main()
