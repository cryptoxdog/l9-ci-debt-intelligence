from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from l9_debt_intelligence.ingestion.storage import (
    FilesystemCorpusStore,
    StorageError,
)


class StorageImmutabilityTests(unittest.TestCase):
    def test_record_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = FilesystemCorpusStore(Path(directory))
            first = {
                "record_id": "cr_" + ("a" * 64),
                "value": 1,
            }
            second = {
                "record_id": "cr_" + ("a" * 64),
                "value": 2,
            }
            store.write_record(first)
            with self.assertRaises(StorageError):
                store.write_record(second)


if __name__ == "__main__":
    unittest.main()
