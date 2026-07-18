# ADR-INTEL-019: Release channels retain previous known-good packs
- Status: Accepted
- Phase: INTEL-P5
## Decision
Defense packs may enter experimental, shadow, or stable channels.
Channel indexes identify an explicit active version and previous known-good
version. Shadow and stable publication require rollback metadata.
Rollback activates the previous immutable pack. It never recompiles or mutates
an existing pack.
