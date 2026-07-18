# ADR-INTEL-022: Closed-loop learning consumes canonical outcome events
- Status: Accepted
- Phase: INTEL-P6
## Decision
Core, LSP, Resolver, and PR Repair emit versioned effectiveness outcome events.
Every event identifies the active defense pack and canonical rule. Producer
implementations remain outside Intelligence.
## Consequences
Intelligence can measure CI, editor, and repair effectiveness without depending
on producer internals.
