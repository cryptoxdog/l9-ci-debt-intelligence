# Roadmap
## INTEL-P0 — Schema federation
Implemented:
- repository ownership boundary;
- immutable SDK schema registry;
- producer compatibility registry;
- corpus event envelope;
- corpus record extension;
- correction and retraction contracts;
- deterministic event hashing;
- quarantine behavior for incompatible producers and contracts;
- architecture tests.
## INTEL-P1 — Reproducible ingestion
Implemented:
- append-only ingestion ledger;
- deterministic event normalization;
- content-addressed corpus records;
- sensitive-content inspection;
- quarantine persistence;
- accepted-record persistence;
- deterministic duplicate observations;
- ingestion store verification.
The Phase 1 filesystem store is a bootstrap implementation, not the final
fleet storage architecture.
## INTEL-P2 — Immutable snapshots
Implemented:
- verified ingestion-store input;
- deterministic snapshot identity;
- immutable Parquet partitions;
- content-addressed snapshot directories;
- partition and record-set hashing;
- deterministic logical manifests;
- snapshot tamper detection;
- derived DuckDB analytical projection.
DuckDB is a rebuildable projection and is not corpus authority.
## INTEL-P3 — Learning metrics
Implemented:
- deterministic analytical observation projection;
- recurrence reports;
- scoped co-occurrence matrices;
- effort atlases with explicit unknown counts;
- false-positive metrics;
- repair-effectiveness metrics;
- deterministic analysis manifests;
- analytical tamper verification.
Analytical reports are derived only from verified immutable snapshots.
## INTEL-P4 — Rule compilation
Implemented:
- deterministic candidate extraction;
- evidence-bounded leverage scoring;
- explicit candidate lifecycle states;
- generated invariant candidates;
- ast-grep candidate output;
- SDK architecture-contract candidate output;
- positive and negative regression fixtures;
- compiler regression results;
- deterministic compiler manifests.
All generated outputs remain non-blocking candidates.
## INTEL-P5 — Signed publication
Implemented:
- immutable `l9.debt-defense/v1` pack assembly;
- promotion-eligible rule selection;
- compatibility matrices;
- deterministic tar-gzip archives;
- Ed25519 detached signatures;
- publication manifests;
- experimental, shadow, and stable channel indexes;
- previous-known-good rollback metadata;
- append-only retirement records;
- immutable GitHub Release publication.
Publication does not mutate Core governance or activate blocking policy.
## INTEL-P6 — Closed-loop effectiveness
Implemented:
- canonical Core CI outcome ingestion;
- canonical LSP outcome ingestion;
- canonical repair outcome ingestion;
- deterministic outcome identities and deduplication;
- rule-level effectiveness measurement;
- pack-level effectiveness measurement;
- explicit unknown and coverage accounting;
- baseline-versus-current drift comparison;
- retain, investigate, rollback, and retirement recommendations;
- minimum-sample recommendation gates;
- immutable effectiveness reports and manifests.
Recommendations remain advisory. Intelligence cannot activate, roll back, or
retire a pack without an explicit action by the responsible authority.
