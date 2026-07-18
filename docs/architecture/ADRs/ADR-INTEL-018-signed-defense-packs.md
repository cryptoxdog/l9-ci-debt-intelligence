# ADR-INTEL-018: Published defense packs require detached signatures
- Status: Accepted
- Phase: INTEL-P5
## Decision
Every published defense-pack archive is signed using an Ed25519 detached
signature over the archive SHA-256 digest.
The publication manifest distributes the signature and raw public verification
key. Private keys remain external secrets and never enter Git or the defense
pack.
## Consequences
Consumers can verify archive integrity and publisher authenticity without
accessing the Intelligence corpus.
