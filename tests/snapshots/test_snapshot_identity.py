from __future__ import annotations

import unittest

from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
)


class SnapshotIdentityTests(unittest.TestCase):
    def test_mapping_order_does_not_change_identity(self) -> None:
        first = namespaced_document_hash(
            "cs_",
            {
                "b": 2,
                "a": 1,
            },
        )
        second = namespaced_document_hash(
            "cs_",
            {
                "a": 1,
                "b": 2,
            },
        )
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("cs_"))
        self.assertEqual(67, len(first))


if __name__ == "__main__":
    unittest.main()
