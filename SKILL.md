---
name: l9-ci-debt-intelligence
description: >-
  Offense/defense intelligence pipeline for CI debt. Ingests findings from
  l9-ci-debt-resolver, builds co-occurrence matrix and effort atlas, generates
  invariants, Copilot instructions, ast-grep rule packs, project scaffolds, and
  PR checklist libraries consumed by l9-ci-debt-lsp and downstream CI consumers.
  Use when: ingesting resolver corpus, running offense/defense pipeline, publishing
  compiled rules, generating scaffolds, or packaging Copilot bundles.
skill_schema: 1
layer: control_plane
role: intelligence_entrypoint
tags: [l9, ci-debt, intelligence, offense, defense, corpus, astgrep, copilot, scaffold]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
---

# L9 CI Debt Intelligence

## Purpose

Transform raw CI debt findings from the resolver into durable prevention and
acceleration artifacts. The pipeline runs in two lanes:

- **Offense** — mine the corpus for patterns, effort costs, and invariants that
  sharpen the resolver and agent context.
- **Defense** — generate Copilot instructions, ast-grep rule packs, project
  scaffolds, and PR checklists that prevent debt from being introduced.

This skill is the intelligence layer between the sensor (resolver) and the
prevention surface (LSP). It does not patch code. It does not push to PRs.
It generates reusable graphable primitives.

## Authority Order

1. Uploaded resolver corpus artifacts (unified_findings.jsonl, convergence report)
2. Adapter for active repo topology (see `adapters/`)
3. References in this skill (protocol contracts, pipeline rules)
4. L9 Compounding Leverage Kernel — score every output before publishing
5. `Unknown` — fail closed; never fabricate corpus data or metrics

## Activation Signals

**Strong (any one triggers):**
- "ingest resolver findings"
- "run offense pipeline" / "run defense pipeline"
- "generate copilot instructions from corpus"
- "publish astgrep pack" / "publish scaffolds"
- "build effort atlas" / "build co-occurrence matrix"

**Reject (do not activate for):**
- Patching code directly — that is the resolver's job
- Pushing fix commits to PRs — use l9-ci-debt-resolver
- Real-time CI log analysis — use l9-ci-debt-resolver
- LSP extension code — use l9-ci-debt-lsp
- Any task requiring invented corpus data

## Pipeline

```
Resolver artifacts
  → Corpus Ingest     (tools/corpus/)
  → Normalize + Merge (tools/corpus/)
      ↓
  Offense Lane        (tools/offense/)
    → Co-occurrence matrix
    → Effort atlas
    → Invariant generation
    → AGENTS.md update
    → Few-shot loader
    → SBOM
      ↓
  Defense Lane        (tools/defense/)
    → Copilot instructions bundle
    → ast-grep rule pack
    → Project scaffolds
    → Diff risk classifier
    → PR checklist library
      ↓
  Packaging           (tools/packaging/)
    → Export pre-commit hook
    → Export ast-grep pack
    → Export scaffolds
    → Export Copilot bundle
      ↓
  Validation          (tools/validation/)
    → Output integrity
    → False-positive rate
    → Topology coverage
```

## Compounding Leverage Gate

Before publishing any output, score it against `references/L9-Leverage.yaml`.
Minimum score to publish: **4.0**. Label unverifiable leverage claims `Unknown`.
Do not publish outputs that score below 3.5 — defer and document the gap.

## Resource Map

Load only when relevant:

- [references/corpus-contract.md](references/corpus-contract.md) — schema and
  ingestion contract for resolver handoff artifacts
- [references/offense-pipeline.md](references/offense-pipeline.md) — co-occurrence,
  effort atlas, invariant, SBOM generation rules
- [references/defense-pipeline.md](references/defense-pipeline.md) — Copilot bundle,
  ast-grep rules, scaffold, checklist generation rules
- [references/deployment-sequencing.md](references/deployment-sequencing.md) — build
  order invariants and cross-repo dependency sequencing
- [references/topology-taxonomy.md](references/topology-taxonomy.md) — CI debt topology
  classes used for coverage validation
- [references/validation-gates.md](references/validation-gates.md) — output validation
  gates before downstream publish
- [references/L9-Leverage.yaml](references/L9-Leverage.yaml) — compounding leverage
  scoring kernel
- [adapters/github-actions.yaml](adapters/github-actions.yaml) — GHA-specific
  behavior overrides
- [adapters/python-uv.yaml](adapters/python-uv.yaml) — Python/uv repo overrides
- [adapters/node-npm.yaml](adapters/node-npm.yaml) — Node/npm repo overrides
- [adapters/polyglot-monorepo.yaml](adapters/polyglot-monorepo.yaml) — monorepo overrides

## Failure Handling

- If resolver artifacts are missing or empty → block, emit `corpus_missing` error,
  do not run pipeline on empty input.
- If a tool script exits non-zero → log failure, mark output as `INVALID`, do not
  package the artifact.
- If leverage score < 3.5 on a generated output → defer, document gap, do not publish.
- If topology coverage < 80% → emit warning, do not claim full coverage.
- Label all unverifiable metrics `Unknown` — never fabricate.

## Dependency Contract

```
l9-ci-debt-resolver  →  emits findings corpus  →  THIS SKILL ingests
THIS SKILL           →  emits compiled rules   →  l9-ci-debt-lsp consumes
```

One-way flow. This skill never calls back into the resolver or the LSP.
