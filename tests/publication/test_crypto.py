from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from l9_debt_intelligence.publication.crypto import (
    generate_keypair,
    sign_digest,
    verify_digest,
)
from l9_debt_intelligence.publication.errors import (
    SignatureVerificationError,
)


class CryptoTests(unittest.TestCase):
    def test_sign_and_verify_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private = root / "private.pem"
            public = root / "public.pem"
            generate_keypair(
                private_key_path=private,
                public_key_path=public,
            )
            signature = sign_digest(
                "a" * 64,
                private,
            )
            verify_digest(
                digest_hex="a" * 64,
                signature=signature.signature,
                public_key=signature.public_key,
            )
            with self.assertRaises(SignatureVerificationError):
                verify_digest(
                    digest_hex="b" * 64,
                    signature=signature.signature,
                    public_key=signature.public_key,
                )


if __name__ == "__main__":
    unittest.main()
