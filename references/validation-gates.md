<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: validation_gates
tags: [validation, gates, output-quality, publish-gate]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
/L9_META -->

# Validation Gates

## Purpose

Prevent publication of invalid, fabricated, or low-quality intelligence
artifacts. All gates must pass before any output is handed to packaging tools.

## Gate Architecture

```
Corpus Validation Gate (CV)
  → Offense Output Gate (OV)
  → Defense Output Gate (DV)
  → Leverage Gate (LV)
  → Topology Coverage Gate (TC)
  → Package Readiness Gate (PR)
```

## Gate CV: Corpus Valid

- [ ] `unified_findings.jsonl` exists and is non-empty.
- [ ] Zero schema violations > 10% threshold.
- [ ] At least 1 `valid_current` finding present.
- [ ] `repo_index.json` and `topology_summary.json` written.

**Block on fail. Do not run offense or defense lanes.**

## Gate OV: Offense Outputs Valid

- [ ] `cooccurrence_matrix.json` exists and passes `schemas/cooccurrence.schema.json`.
- [ ] `effort_atlas.json` exists and passes `schemas/effort_atlas.schema.json`.
- [ ] `generated_invariants.yaml` exists and passes `schemas/invariant.schema.json`.
- [ ] No `Unknown` values in effort_atlas fields that have direct corpus evidence.
- [ ] `sbom.cdx.json` is valid CycloneDX 1.4.

**Warn on fail. Log invalid artifacts. Do not publish failing artifacts.**

## Gate DV: Defense Outputs Valid

- [ ] `copilot-instructions.md` exists and has at least 1 instruction block.
- [ ] At least 1 ast-grep rule YAML exists in `outputs/defense/astgrep/rules/`.
- [ ] `sgconfig.yml` lists all rule files.
- [ ] At least 1 scaffold directory exists in `outputs/defense/scaffolds/`.
- [ ] `checklist_library.yaml` exists and has at least 1 topology block.

**Warn on fail. Log missing artifacts.**

## Gate LV: Leverage Score

- [ ] Each published artifact has a logged leverage score >= 4.0.
- [ ] Scaffolds have leverage score >= 4.5.
- [ ] No artifact published without a leverage score.

**Block publication of artifacts without leverage score. Log as `leverage_unknown`.**

## Gate TC: Topology Coverage

- [ ] Coverage >= 80% (5 of 7 active topology classes).
- [ ] Coverage percentage logged in `outputs/corpus/topology_summary.json`.

**Warn if < 80%. Do not block. Include coverage warning in package manifest.**

## Gate PR: Package Readiness

- [ ] All CV, OV, DV, LV gates passed (or explicitly warned with documented gaps).
- [ ] `MANIFEST.md` updated with output artifact list.
- [ ] No stub or placeholder files in outputs/.
- [ ] All `Unknown` values labeled, not omitted.

**Block zip/publish if any gate is in BLOCK state.**
