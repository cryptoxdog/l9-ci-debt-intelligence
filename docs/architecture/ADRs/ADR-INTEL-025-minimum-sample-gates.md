# ADR-INTEL-025: Rollback and retirement recommendations require minimum samples
- Status: Accepted
- Phase: INTEL-P6
## Decision
Rule-level recommendations require at least 20 observations. Pack-level
recommendations require at least 100 observations.
Below those thresholds the state is `insufficient_evidence`, even when the
observed ratio appears poor.
## Consequences
Small-sample noise cannot automatically escalate to rollback or retirement.
