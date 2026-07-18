# ADR-INTEL-006: Corpus ingestion is deterministic and content-addressed
- Status: Accepted
- Phase: INTEL-P1
## Context
Producer events may be redelivered, reordered, or observed by multiple
ingestion workers. Corpus identity cannot depend on arrival order.
## Decision
Corpus record identity is derived from:
- producer identity;
- producer contract;
- event class;
- snapshot or run identity;
- normalized payload hash.
Repeated observations of the same logical record append ledger entries but do
not create additional corpus records.
## Consequences
Arrival timestamps and ledger sequence numbers identify observations, not
corpus records.
A record identity collision with a different normalized payload is quarantined.
