from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SchemaFederationTests(unittest.TestCase):
    def test_sdk_registry_is_pinned(self) -> None:
        registry = json.loads(
            (ROOT / ".l9/sdk-schema-registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            "c78486ea9b7d596d0b6db755b5780e5289878d35",
            registry["sdk"]["revision"],
        )
        self.assertFalse(registry["policy"]["local_schema_copies_allowed"])

    def test_intelligence_schemas_do_not_define_sdk_findings(self) -> None:
        prohibited = {
            "canonical_rule_id",
            "provider_rule_id",
            "finding_id",
            "evidence_id",
            "source_location",
        }
        phase_1_schemas = (
            "corpus-event.schema.json",
            "corpus-record.schema.json",
            "corpus-correction.schema.json",
            "corpus-retraction.schema.json",
            "validation-result.schema.json",
        )
        for schema_name in phase_1_schemas:
            schema = ROOT / "schemas/intelligence" / schema_name
            with self.subTest(schema=schema.name):
                document = json.loads(schema.read_text(encoding="utf-8"))
                properties = set(document.get("properties", {}))
                self.assertTrue(prohibited.isdisjoint(properties))


if __name__ == "__main__":
    unittest.main()
