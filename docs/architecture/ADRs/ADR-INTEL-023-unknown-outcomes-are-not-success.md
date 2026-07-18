# ADR-INTEL-023: Unknown or incomplete outcomes are not successful outcomes
- Status: Accepted
- Phase: INTEL-P6
## Decision
`rule_not_evaluated`, `evaluation_incomplete`, and `outcome_unknown` remain
explicit unknown observations.
They cannot increase prevention, repair-success, or quality scores.
## Consequences
Incomplete telemetry lowers evidence coverage rather than producing false
success.
