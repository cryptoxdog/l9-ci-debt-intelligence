# ADR-INTEL-017: Every compiled candidate requires regression fixtures
- Status: Accepted
- Phase: INTEL-P4
## Decision
Every non-deferred candidate receives positive and negative fixtures.
Compilation fails when any generated fixture fails.
Later compiler adapters may add language-specific fixtures without weakening
this minimum.
