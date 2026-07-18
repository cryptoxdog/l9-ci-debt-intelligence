# ADR-INTEL-011: DuckDB is a derived analytical projection
- Status: Accepted
- Phase: INTEL-P2
## Decision
DuckDB reads immutable snapshot Parquet partitions and exposes a deterministic
`corpus_records` view.
DuckDB files are rebuildable projections. They are not the corpus authority and
must not mutate source snapshot partitions.
