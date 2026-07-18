# ADR-INTEL-007: Phase 2 uses a bootstrap filesystem store
- Status: Accepted
- Phase: INTEL-P1
## Context
The target corpus architecture uses versioned object storage, Parquet, and
DuckDB. Those components belong to INTEL-P2.
## Decision
INTEL-P1 implements the ingestion protocol using an append-only JSONL ledger
and immutable content-addressed JSON objects.
This backend is suitable for contract validation, local operation, and
determinism tests. It is not the final fleet corpus storage system.
## Consequences
Storage interfaces must remain independent of analytics and snapshot formats.
