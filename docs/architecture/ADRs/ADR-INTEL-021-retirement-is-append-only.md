# ADR-INTEL-021: Defense-pack retirement is append-only
- Status: Accepted
- Phase: INTEL-P5
## Decision
Retirement creates a signed-lineage retirement record containing the pack
identity, archive digest, reason, issuer, time, and optional replacement.
Existing release artifacts and publication history remain available for audit
and rollback analysis.
