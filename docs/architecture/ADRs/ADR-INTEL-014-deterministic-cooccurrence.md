# ADR-INTEL-014: Co-occurrence is scoped and set-based
- Status: Accepted
- Phase: INTEL-P3
## Decision
Two recurrence fingerprints co-occur when both are present in the same
occurrence scope.
Pairs are unordered. Self-pairs are excluded. Repeated observations of one
fingerprint in the same scope count once.
## Consequences
Arrival order and duplicate delivery cannot inflate co-occurrence.
