# ADR-INTEL-013: Missing analytical dimensions remain unknown
- Status: Accepted
- Phase: INTEL-P3
## Decision
Missing effort, validation outcomes, rule identities, and false-positive
dispositions are represented as null and counted as unknown.
They are never interpreted as zero, failure, success, true-positive, or
false-positive.
## Consequences
Reports contain known and unknown counts, and ratios use only observations with
the required known classifications.
