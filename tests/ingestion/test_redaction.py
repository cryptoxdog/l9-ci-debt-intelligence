from __future__ import annotations

import unittest

from l9_debt_intelligence.ingestion.redaction import (
    assess_redaction,
)


class RedactionTests(unittest.TestCase):
    def test_sensitive_key_is_detected(self) -> None:
        result = assess_redaction(
            {
                "redaction_status": "producer_redacted",
                "payload": {
                    "api_token": "value",
                },
            }
        )
        self.assertFalse(result.safe)
        self.assertEqual("sensitive_content", result.reason)

    def test_absolute_path_is_detected(self) -> None:
        result = assess_redaction(
            {
                "redaction_status": "producer_redacted",
                "payload": {
                    "message": "failed in /home/user/project/main.py",
                },
            }
        )
        self.assertFalse(result.safe)

    def test_safe_reference_is_allowed(self) -> None:
        result = assess_redaction(
            {
                "redaction_status": "producer_redacted",
                "payload": {
                    "artifact_reference": "artifact://run-100",
                },
            }
        )
        self.assertTrue(result.safe)


if __name__ == "__main__":
    unittest.main()
