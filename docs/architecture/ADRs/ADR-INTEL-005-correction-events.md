# ADR-INTEL-005: Corpus history uses correction and retraction events
- Status: Accepted
- Phase: INTEL-P0
## Decision
Historical records are never silently overwritten.
Corrections identify the target record and replacement event. Retractions
identify the target record, issuer, timestamp, and reason. Consumers reconstruct
the current logical view from the append-only event history.
