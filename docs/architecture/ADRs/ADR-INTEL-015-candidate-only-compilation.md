# ADR-INTEL-015: Compiled prevention rules remain candidates
- Status: Accepted
- Phase: INTEL-P4
## Decision
INTEL-P4 compiler outputs are candidate artifacts. They cannot independently
enable blocking policy, promote themselves, mutate repositories, or execute
external commands.
Promotion belongs to later signed publication and Core governance.
