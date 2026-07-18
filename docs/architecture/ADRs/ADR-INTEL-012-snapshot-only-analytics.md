# ADR-INTEL-012: Learning metrics consume verified snapshots only
- Status: Accepted
- Phase: INTEL-P3
## Decision
Authoritative learning metrics are derived from verified immutable corpus
snapshots.
Analytics does not read mutable ingestion state, raw logs, repository source,
or legacy generated outputs.
## Consequences
Every report identifies one source snapshot and is reproducible from that
snapshot.
