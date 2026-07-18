# ADR-INTEL-001: Intelligence owns the canonical fleet corpus
- Status: Accepted
- Phase: INTEL-P0
## Decision
`l9-ci-debt-intelligence` owns historical fleet corpus records and
Intelligence-specific schema extensions.
SDK evidence, findings, source locations, snapshots, validation results, and
coverage remain SDK-owned contracts. Intelligence references those contracts;
it does not duplicate them.
## Consequences
Producer payloads retain their public contract identity. Intelligence records
lineage, lifecycle, redaction state, limitations, and correction history
around those payloads.
