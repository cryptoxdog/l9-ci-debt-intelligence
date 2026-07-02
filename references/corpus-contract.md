<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: corpus_contract
tags: [corpus, ingestion, schema, resolver-handoff]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
/L9_META -->

# Corpus Contract

## Purpose

Defines the schema and ingestion contract for artifacts handed off from
l9-ci-debt-resolver to l9-ci-debt-intelligence.

## Upstream Artifacts

### Primary: `PR_REMEDIATION_FINDINGS.jsonl`

One JSONL record per finding. Each record must conform to this schema:

```json
{
  "pr": "<integer>",
  "cycle": "<integer>",
  "finding_id": "<string: e.g. CI-IMPORT-001-pr3-c1>",
  "source": "<string: gha_log | coderabbit_inline | coderabbit_walkthrough | manual>",
  "severity": "<string: critical | high | medium | low>",
  "classification": "<string: valid_current | unknown | doctrine_reject | out_of_scope>",
  "location": "<string: file:line or 'repo-wide'>",
  "description": "<string>",
  "action": "<string: patch | not_patched>",
  "rule_id": "<string: e.g. CI-IMPORT-001 | null>",
  "topology": "<string: gha_workflow | python_deps | api_drift | test_isolation | null>",
  "resolved": "<boolean>",
  "commit_sha": "<string | null>"
}
```

### Secondary: `PR_REMEDIATION_CONVERGENCE_REPORT.md`

Used to extract per-PR cycle counts, convergence status, and known blockers.
Parsed by `tools/corpus/ingest_findings.py` into `outputs/corpus/repo_index.json`.

### Gate artifacts (optional)

`gate_artifacts/pr_<N>_cycle_<C>/` directories. Parsed to extract local gate
results (A/B/C/D pass rates) for the effort atlas.

## Validation Rules

- Every record must have `pr`, `finding_id`, `classification`, `description`.
- Records with `classification: unknown` are included in corpus but excluded
  from invariant generation.
- Records with `classification: doctrine_reject` are included in corpus and
  flagged in the SBOM.
- `rule_id: null` is allowed — classify as `topology: unclassified`.
- Duplicate `finding_id` values are deduplicated; last write wins.

## Output of Ingestion

After `ingest_findings.py` + `normalize_corpus.py` run:

```
outputs/corpus/
  unified_findings.jsonl      <- normalized, deduplicated, schema-validated
  repo_index.json             <- per-repo/per-PR metadata summary
  topology_summary.json       <- counts by topology class
```

## Reject Conditions

- Empty or missing JSONL file → block pipeline, emit `corpus_missing`.
- JSONL with zero `valid_current` records → warn, do not run offense lane.
- Schema violations > 10% of records → block, emit `corpus_corrupt`.
