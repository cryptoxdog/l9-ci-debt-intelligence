from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from l9_debt_intelligence.publication.channels import (
    update_channel,
)


def manifest(
    *,
    version: str,
    pack_id: str,
    digest: str,
) -> dict:
    return {
        "schema_version": "l9.defense-publication/v1",
        "pack_id": pack_id,
        "pack_version": version,
        "archive_name": "pack.tar.gz",
        "archive_sha256": digest,
        "archive_size": 1,
        "signature": "signature",
        "public_key": "public-key",
        "signature_algorithm": "Ed25519",
        "channel": "experimental",
        "rollback": {
            "available": False,
            "previous_pack_version": None,
            "previous_pack_sha256": None,
        },
        "publication_gates": {"schema_valid": True},
    }


class ChannelTests(unittest.TestCase):
    def test_channel_retains_previous_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "experimental.json"
            first_path = root / "first.json"
            first_path.write_text(
                json.dumps(
                    manifest(
                        version="1.0.0",
                        pack_id="pack_" + ("a" * 64),
                        digest="b" * 64,
                    )
                )
            )
            second_path = root / "second.json"
            second_path.write_text(
                json.dumps(
                    manifest(
                        version="1.1.0",
                        pack_id="pack_" + ("c" * 64),
                        digest="d" * 64,
                    )
                )
            )
            update_channel(
                channel="experimental",
                publication_manifest_path=first_path,
                channel_index_path=index,
            )
            result = update_channel(
                channel="experimental",
                publication_manifest_path=second_path,
                channel_index_path=index,
            )
            self.assertEqual(
                "1.1.0",
                result["active"]["pack_version"],
            )
            self.assertEqual(
                "1.0.0",
                result["previous"]["pack_version"],
            )


if __name__ == "__main__":
    unittest.main()
