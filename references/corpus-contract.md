<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: corpus_contract
tags: [corpus, ingestion, schema, resolver-handoff]
owner: igor_beylin
status: active
version: 1.1.0
updated: 2026-07-03
/L9_META -->

# Corpus Contract

## Purpose

Defines the schema and ingestion contract for artifacts handed off from
l9-ci-debt-resolver to l9-ci-debt-intelligence.

## Upstream Handoff

Resolver (`Quantum-L9/l9-ci-debt-resolver`) triggers this repo via
`repository_dispatch` event `ci_debt_resolver_corpus_ready`. The dispatch
`client_payload` carries `source_repo`, `run_id`, `run_attempt`, `source_sha`,
and `artifact_name` (`ci-debt-resolver-corpus`). `corpus-update.yml` downloads
that artifact from the resolver run using `L9_RESOLVER_READ_TOKEN`.

### Artifact: `ci-debt-resolver-corpus`

| File | Purpose |
|---|---|
| `CI_DEBT_FINDINGS.jsonl` | one resolver finding per line (ingested) |
| `REMEDIATION_TRACES.jsonl` | per-run remediation traces (provenance) |
| `CORPUS_MANIFEST.json` | producer, source repo/sha, run id, row counts, sha256 |

### Primary: `CI_DEBT_FINDINGS.jsonl` (resolver schema)

Each record conforms to the resolver's
`schemas/ci_debt_finding.schema.json`. Required fields:

```json
{
  "schema_version": "1.0",
  "source": "l9-ci-debt-resolver",
  "repo": "<owner/name>",
  "finding_id": "<string>",
  "failure_type": "<string: resolver category id>",
  "root_cause": "<string>",
  "outcome": "<string: repaired | failed | blocked | unknown | observed>",
  "created_at": "<ISO-8601 string>"
}
```

### Resolver -> Corpus mapping (`map_resolver_findings.py`)

Resolver findings are deterministically mapped to `schemas/corpus.schema.json`
before ingest. Every corpus field traces to a resolver field or a documented
default; no finding data is invented.

| Corpus field | Derivation |
|---|---|
| `finding_id` | `finding_id` |
| `repo` | `repo` |
| `rule_id` | `failure_type` (else `UNKNOWN`) |
| `tenant_id` | repo owner (before `/`), else repo, else `unknown` |
| `classification` | `outcome` = `unknown`/absent -> `unknown`; else `valid_current` |
| `action` | `outcome` = `repaired` -> `patch`; else `not_patched` |
| `source` | `gha_log` (resolver findings derive from GHA logs) |
| `ci_system` | existing `ci_system`, else `github-actions` |
| `language` | existing `language`, else `unknown` |
| `pr` | `pr_number` when present |

The resolver's `source` constant is retained as `resolver_source`; all other
resolver fields are preserved for provenance (`additionalProperties: true`).

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
