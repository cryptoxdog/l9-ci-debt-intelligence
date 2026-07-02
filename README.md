# l9-ci-debt-intelligence

Offense/defense intelligence pipeline for CI debt. Part of the L9 CI debt
elimination system.

## Role in the three-repo system

```
l9-ci-debt-resolver   ← sensor: fixes PRs, emits findings corpus
l9-ci-debt-intelligence  ← this repo: mines corpus, generates prevention artifacts
l9-ci-debt-lsp        ← prevention: IDE-time diagnostics and quick fixes
```

## What this repo produces

| Output | Location | Consumer |
|---|---|---|
| Co-occurrence matrix | `outputs/offense/cooccurrence_matrix.json` | Resolver context |
| Effort atlas | `outputs/offense/effort_atlas.json` | Corp dev proof |
| Invariants | `outputs/offense/generated_invariants.yaml` | Resolver AGENTS.md |
| Copilot instructions | `outputs/defense/copilot/copilot-instructions.md` | LSP + IDE |
| ast-grep rules | `outputs/defense/astgrep/rules/*.yaml` | LSP + pre-commit |
| Project scaffolds | `outputs/defense/scaffolds/` | New repo bootstrap |
| PR checklist lib | `outputs/defense/pr-checklists/checklist_library.yaml` | PR review |
| SBOM | `outputs/offense/sbom/sbom.cdx.json` | Compliance diligence |

## Running the pipeline

```bash
# 1. Drop resolver artifacts into the corpus input dir
cp path/to/PR_REMEDIATION_FINDINGS.jsonl corpus_input/

# 2. Ingest and normalize
python tools/corpus/ingest_findings.py --input corpus_input/ --output outputs/corpus/
python tools/corpus/normalize_corpus.py --corpus outputs/corpus/unified_findings.jsonl

# 3. Offense lane
python tools/offense/build_cooccurrence_matrix.py
python tools/offense/build_effort_atlas.py
python tools/offense/corpus_to_invariants.py

# 4. Defense lane
python tools/defense/copilot_instructions_generator.py
python tools/defense/corpus_to_astgrep.py
python tools/defense/scaffold_generator.py
python tools/defense/checklist_library_builder.py

# 5. Validate
python tools/validation/validate_outputs.py
python tools/validation/validate_topology_coverage.py

# 6. Package
python tools/packaging/export_astgrep_pack.py
python tools/packaging/export_copilot_bundle.py
python tools/packaging/export_scaffolds.py
```

## Leverage gate

Every generated artifact is scored against `references/L9-Leverage.yaml`.
Artifacts scoring below 4.0 are deferred, not published.

## Invariants

- This repo never patches code.
- This repo never pushes commits to other repos' PRs.
- Corpus data is never fabricated — missing data is labeled `Unknown`.
- All outputs must be graphable primitives (schema-validated JSON/YAML).
- One-way dependency flow is enforced: resolver → this repo → LSP.
