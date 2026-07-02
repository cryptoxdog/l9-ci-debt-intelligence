<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: offense_pipeline
tags: [offense, cooccurrence, effort-atlas, invariants, sbom, agents-md]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
/L9_META -->

# Offense Pipeline

## Purpose

Mine the normalized corpus to produce intelligence products that sharpen the
resolver's doctrine, reduce agent context waste, and generate compliance proof
artifacts.

## Tool Sequence

```
normalized corpus
  → build_cooccurrence_matrix.py   → outputs/offense/cooccurrence_matrix.json
  → build_effort_atlas.py          → outputs/offense/effort_atlas.json
  → corpus_to_invariants.py        → outputs/offense/generated_invariants.yaml
  → agents_md_updater.py           → outputs/offense/CONTEXT_PRIMERS.md
  → few_shot_loader.py             → outputs/offense/few_shot_examples.yaml
  → sbom_from_findings.py          → outputs/offense/sbom/sbom.cdx.json
```

## Rules per Tool

### build_cooccurrence_matrix.py
- Count co-occurrence of (rule_id, topology) pairs across all findings.
- Normalize by PR count to get per-PR frequency.
- Output: square matrix keyed by rule_id, values are co-occurrence counts.
- Minimum corpus size to run: 10 valid_current findings.
- If corpus < 10 findings: emit `corpus_too_small`, skip matrix.

### build_effort_atlas.py
- For each rule_id, compute: occurrence_count, avg_cycles_to_fix,
  avg_gate_failures_before_green, PRs_affected.
- Derive effort_score = occurrence_count * avg_cycles_to_fix.
- Sort descending by effort_score.
- Output: effort_atlas.json conforming to schemas/effort_atlas.schema.json.
- Label any metric without direct corpus evidence as `Unknown`.

### corpus_to_invariants.py
- For each rule_id with occurrence_count >= 3: generate a candidate invariant.
- Invariant format: { rule_id, condition, invariant_statement, evidence_count,
  confidence: high|medium|low|Unknown }
- confidence: high if evidence_count >= 5, medium if >= 3, Unknown if < 3.
- Output: generated_invariants.yaml conforming to schemas/invariant.schema.json.
- Do not generate invariants for `classification: unknown` findings.

### agents_md_updater.py
- Produce CONTEXT_PRIMERS.md: a set of compact context blocks for injection
  into resolver AGENTS.md.
- One primer per high-confidence invariant.
- Format: YAML block with rule_id, primer_text (max 3 sentences), evidence_count.
- Do not inject primers with confidence: Unknown.

### few_shot_loader.py
- Select top-5 findings by effort_score where action == patch and resolved == true.
- Extract: finding description, patch summary, gate results, commit sha.
- Format as few-shot examples for agent context.
- Output: few_shot_examples.yaml.

### sbom_from_findings.py
- Generate a CycloneDX 1.4 SBOM listing all rule_ids found in corpus.
- Include: rule_id, topology, occurrence_count, doctrine_reject_count.
- Flag any rule_id with doctrine_reject_count > 0 as `risk: elevated`.
- Output: sbom.cdx.json.

## Leverage Gate

Before publishing any offense output, score against L9-Leverage.yaml.
Minimum publish score: 4.0. Log score in output file header comment.
