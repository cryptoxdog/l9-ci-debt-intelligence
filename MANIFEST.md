# Manifest — l9-ci-debt-intelligence

version: 1.0.0
updated: 2026-07-02
status: initial

## Upstream Dependency

| Artifact | Source repo | Contract |
|---|---|---|
| `unified_findings.jsonl` | l9-ci-debt-resolver | references/corpus-contract.md |
| `PR_REMEDIATION_CONVERGENCE_REPORT.md` | l9-ci-debt-resolver | references/corpus-contract.md |

## Downstream Consumers

| Artifact | Consumer repo | Notes |
|---|---|---|
| `outputs/defense/astgrep/rules/*.yaml` | l9-ci-debt-lsp | Loaded by rules_loader.py |
| `outputs/defense/copilot/copilot-instructions.md` | l9-ci-debt-lsp | Injected into VS Code bundle |
| `outputs/defense/scaffolds/` | l9-ci-debt-lsp + CI consumers | Project bootstrap templates |
| `outputs/offense/generated_invariants.yaml` | l9-ci-debt-resolver AGENTS.md | Tightens resolver doctrine |
| `outputs/offense/effort_atlas.json` | Corp dev proof artifacts | Demonstrates measurable CI debt cost |

## File Inventory

```
SKILL.md
MANIFEST.md
README.md
CHANGE_SUMMARY.md
references/
  corpus-contract.md
  offense-pipeline.md
  defense-pipeline.md
  deployment-sequencing.md
  topology-taxonomy.md
  validation-gates.md
  L9-Leverage.yaml
tools/
  corpus/
    ingest_findings.py
    normalize_corpus.py
    merge_repo_runs.py
    validate_corpus.py
  offense/
    build_cooccurrence_matrix.py
    build_effort_atlas.py
    corpus_to_invariants.py
    agents_md_updater.py
    few_shot_loader.py
    sbom_from_findings.py
  defense/
    copilot_instructions_generator.py
    corpus_to_astgrep.py
    scaffold_generator.py
    diff_risk_classifier.py
    checklist_library_builder.py
  packaging/
    export_precommit_hook.py
    export_astgrep_pack.py
    export_scaffolds.py
    export_copilot_bundle.py
  validation/
    validate_outputs.py
    validate_false_positive_rate.py
    validate_topology_coverage.py
schemas/
  corpus.schema.json
  effort_atlas.schema.json
  cooccurrence.schema.json
  invariant.schema.json
adapters/
  github-actions.yaml
  python-uv.yaml
  node-npm.yaml
  polyglot-monorepo.yaml
outputs/
  corpus/.gitkeep
  offense/.gitkeep
  defense/.gitkeep
.github/workflows/
  corpus-update.yml
  publish-astgrep-pack.yml
  publish-scaffolds.yml
  validate-intelligence-outputs.yml
```

Total: 47 files (43 source + 3 .gitkeep + 1 schemas placeholder)
