# ADR-INTEL-009: Corpus snapshots are immutable and content-addressed
- Status: Accepted
- Phase: INTEL-P2
## Decision
A snapshot identity is derived from the ordered accepted-record set, record
hashes, partition plan, snapshot format version, and SDK contract version.
Build time, machine identity, process identity, and filesystem location do not
participate in snapshot identity.
Existing snapshots are never overwritten. Corrections create new snapshots.
## Consequences
The same verified record set and implementation contract resolve to the same
snapshot identifier.
Snapshot verification includes every partition hash and the deterministic
logical-manifest hash.
