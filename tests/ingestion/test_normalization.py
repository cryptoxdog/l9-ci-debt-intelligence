from __future__ import annotations

import unittest

from l9_debt_intelligence.ingestion.normalization import (
    NormalizationError,
    normalize_event,
    normalized_payload_hash,
)


class NormalizationTests(unittest.TestCase):
    def test_mapping_order_does_not_change_hash(self) -> None:
        first = {
            "payload": {
                "b": 2,
                "a": 1,
            }
        }
        second = {
            "payload": {
                "a": 1,
                "b": 2,
            }
        }
        self.assertEqual(
            normalized_payload_hash(first),
            normalized_payload_hash(second),
        )

    def test_limitations_are_sorted_and_unique(self) -> None:
        event = normalize_event(
            {
                "limitations": ["z", "a", "z"],
                "payload": {},
            }
        )
        self.assertEqual(["a", "z"], event["limitations"])

    def test_float_is_rejected(self) -> None:
        with self.assertRaises(NormalizationError):
            normalize_event(
                {
                    "payload": {
                        "confidence": 0.5,
                    }
                }
            )


if __name__ == "__main__":
    unittest.main()
