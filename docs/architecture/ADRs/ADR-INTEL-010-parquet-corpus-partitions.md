# ADR-INTEL-010: Normalized snapshot records are stored as Parquet
- Status: Accepted
- Phase: INTEL-P2
## Decision
Snapshot records are partitioned by event class and producer identity, ordered
by canonical record identity, and encoded as Parquet using Zstandard
compression.
Parquet files contain normalized corpus metadata and content hashes. They do
not contain producer source code, raw logs, credentials, or absolute paths.
