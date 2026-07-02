<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: topology_taxonomy
tags: [topology, classification, ci-debt, coverage]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
/L9_META -->

# Topology Taxonomy

## Purpose

Classify all CI debt findings into topology classes. Coverage is measured
against this taxonomy. A pipeline run that covers < 80% of active topology
classes emits a coverage warning.

## Active Topology Classes

| topology | description | known rule_ids |
|---|---|---|
| `gha_workflow` | GitHub Actions workflow misconfiguration | CI-IMPORT-001, CI-DEPS-002 |
| `python_deps` | Missing or incorrect Python package dependencies | CI-DEPS-001 |
| `api_drift` | Python module/class API drift between implementation and tests | API-DRIFT-001 |
| `test_isolation` | Test collection failures due to missing chassis or environment | (resolver: unknown/structural) |
| `doctrine_violation` | PacketEnvelope / non-TransportPacket wire format usage | (resolver: doctrine_reject) |
| `semantic_tolerance` | Aggregate scripts with insufficient semantic tolerance | (resolver: aggregate.py class) |
| `unclassified` | Findings with no assigned rule_id or topology | any |

## Coverage Calculation

```
coverage = (topology classes with >= 1 valid_current finding) / (total active topology classes)
```

Minimum acceptable coverage: **80%** (5 of 7 active classes represented).

## Adding New Topology Classes

When a new finding type appears in the corpus that does not match any existing
class:

1. Add a new row to this table with a proposed topology name.
2. Assign a rule_id if the pattern is deterministic.
3. Update `schemas/corpus.schema.json` to include the new topology enum value.
4. Re-run `validate_topology_coverage.py` to confirm coverage recalculation.

## Reject Condition

Do not publish offense or defense outputs for a topology class with fewer than
2 valid_current findings. Label as `insufficient_evidence`.
