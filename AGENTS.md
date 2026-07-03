# AGENTS.md — l9-ci-debt-intelligence

<!-- JUSTIFICATION (wire/intelligence-corpus-ingest): wiring contract corrected to
     match the live resolver dispatch. Resolver emits repository_dispatch event
     `ci_debt_resolver_corpus_ready` (not `corpus-update`/`resolver-run-complete`)
     with artifact `ci-debt-resolver-corpus` (CI_DEBT_FINDINGS.jsonl,
     REMEDIATION_TRACES.jsonl, CORPUS_MANIFEST.json). Repo owner is Quantum-L9.
     Resolver findings are mapped to corpus schema by map_resolver_findings.py. -->

## Role in the three-repo system

```
l9-ci-debt-resolver  →  l9-ci-debt-intelligence  →  l9-ci-debt-lsp
      (sensor)               (corpus + rules)            (IDE surface)
```

**Upstream:** `Quantum-L9/l9-ci-debt-resolver` uploads artifact `ci-debt-resolver-corpus` (`CI_DEBT_FINDINGS.jsonl`, `REMEDIATION_TRACES.jsonl`, `CORPUS_MANIFEST.json`) and triggers this repo via `repository_dispatch` event `ci_debt_resolver_corpus_ready`.
**Downstream:** `Quantum-L9/l9-ci-debt-lsp` consumes compiled rules published by `publish-astgrep-pack` as a GitHub release artifact.

## Authority order
1. This file (`AGENTS.md`) — operating contract, supersedes all other instructions
2. `references/` docs — pipeline contracts, schema contracts, topology rules
3. `schemas/` JSON schemas — output format enforcement
4. Adapter YAMLs in `adapters/` — per-ecosystem overrides
5. Tool docstrings — implementation notes only

## What this repo does
- Ingests resolver findings corpus
- Normalizes, merges, and validates the corpus
- Generates offense artifacts: co-occurrence matrix, effort atlas, invariants, CONTEXT_PRIMERS.md, SBOM
- Generates defense artifacts: Copilot instructions, ast-grep rules, scaffolds, checklist library
- Packages and publishes compiled rules for LSP consumption
- Validates all outputs against schemas and false-positive thresholds

## Allowed actions
- Run any tool in `tools/` against corpus in `outputs/corpus/`
- Write to `outputs/` subdirectories
- Update `schemas/` to add fields (never remove)
- Update adapter YAMLs to add or extend `scaffold_files` content
- Append to `CHANGE_SUMMARY.md`
- Commit and push to `main` when all four local gates pass
- Open a PR to `main` from a feature branch

## Forbidden actions
- Force-push to any branch
- Weaken any validation gate (lower thresholds, skip schema checks, comment out assertions)
- Invent corpus data — every finding must trace to a real resolver output or a declared fixture
- Fabricate benchmark numbers or test pass claims
- Delete files from `references/` or `schemas/`
- Modify `AGENTS.md` without a written justification comment in the same commit
- Publish a release artifact without `validate-intelligence-outputs` workflow passing
- Use a GPL/AGPL dependency without legal sign-off noted in the commit message

## Local gate protocol (all four must pass before commit)
```bash
# A — compile
python -m compileall tools/ -q

# B — lint
ruff check tools/ schemas/

# C — tests
pytest tests/ -q

# D — schema validate outputs
python tools/validation/validate_outputs.py
```
Record each gate result as PASS / FAIL / UNRESOLVED in the commit message.
Do NOT commit if any gate is FAIL.
UNRESOLVED is permitted only for structural blockers (missing upstream corpus) — note the reason.

## Pipeline execution order
```
map_resolver_findings       # resolver schema -> corpus schema (deterministic)
  → ingest_findings
  → normalize_corpus
  → merge_repo_runs
  → validate_corpus          # abort if corpus invalid
  → build_cooccurrence_matrix
  → build_effort_atlas
  → corpus_to_invariants
  → agents_md_updater
  → few_shot_loader
  → sbom_from_findings
  → copilot_instructions_generator
  → corpus_to_astgrep
  → scaffold_generator
  → diff_risk_classifier
  → checklist_library_builder
  → export_precommit_hook
  → export_astgrep_pack
  → export_scaffolds
  → export_copilot_bundle
  → validate_outputs
  → validate_false_positive_rate
  → validate_topology_coverage
```

## Wiring contract

### Trigger (from resolver)
Listens for `repository_dispatch` event `ci_debt_resolver_corpus_ready`.
`corpus-update.yml` reads `client_payload.source_repo` and `client_payload.run_id`,
downloads artifact `ci-debt-resolver-corpus` from that resolver run using
`L9_RESOLVER_READ_TOKEN`, maps `CI_DEBT_FINDINGS.jsonl` to corpus schema via
`map_resolver_findings.py`, then ingests. Manual `workflow_dispatch` accepts
`source_repo` and `run_id` inputs for the same path.

### Publish (to LSP)
`publish-astgrep-pack.yml` creates a GitHub release tagged `rules-<sha>` containing:
- `astgrep-pack.tar.gz` — all ast-grep rules
- `compiled_rules.json` — LSP-consumable flattened rule set
- `VALIDATION.md` — proof artifact

## Handoff artifacts

| Artifact | Path | Consumer |
|---|---|---|
| Unified findings corpus | `outputs/corpus/unified_findings.jsonl` | offense tools |
| Co-occurrence matrix | `outputs/offense/cooccurrence_matrix.json` | effort atlas |
| Effort atlas | `outputs/offense/effort_atlas.json` | invariant generator |
| Generated invariants | `outputs/offense/generated_invariants.yaml` | AGENTS.md updater, LSP |
| CONTEXT_PRIMERS.md | `outputs/offense/CONTEXT_PRIMERS.md` | resolver agent prompts |
| Copilot instructions | `outputs/defense/copilot/copilot-instructions.md` | GitHub Copilot |
| ast-grep rules | `outputs/defense/astgrep/rules/*.yaml` | LSP, pre-commit |
| Scaffolds | `outputs/defense/scaffolds/` | new-repo bootstrap |
| Checklist library | `outputs/defense/pr-checklists/checklist_library.yaml` | PR templates |
| SBOM | `outputs/offense/sbom/sbom.cdx.json` | SOC 2 evidence |

## Secrets required

| Secret | Purpose | Required for |
|---|---|---|
| `L9_RESOLVER_READ_TOKEN` | Read resolver artifacts from GHA runs | `corpus-update.yml` |
| `L9_LSP_DISPATCH_TOKEN` | Trigger LSP refresh after publish | `publish-astgrep-pack.yml` |
| `GITHUB_TOKEN` | Standard actions token | all workflows (auto-provided) |

## Schema invariants
- Every finding record must conform to `schemas/corpus.schema.json`
- A finding classification of `doctrine_reject` must never produce an ast-grep rule or scaffold
- A finding classification of `unknown` must never contribute to co-occurrence counts

## Tenant isolation note
If corpus data from multiple customers is ingested, `normalize_corpus.py` must tag each finding with `tenant_id` before merge. `merge_repo_runs.py` must never mix findings across tenants without explicit `--tenant-merge` flag.
