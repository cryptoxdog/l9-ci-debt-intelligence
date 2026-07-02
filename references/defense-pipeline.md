<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: defense_pipeline
tags: [defense, copilot, astgrep, scaffold, checklist, diff-risk]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
/L9_META -->

# Defense Pipeline

## Purpose

Generate IDE-time and review-time prevention artifacts from the normalized
corpus. Defense artifacts are consumed by l9-ci-debt-lsp and CI workflows.

## Tool Sequence

```
normalized corpus + effort atlas
  → copilot_instructions_generator.py  → outputs/defense/copilot/copilot-instructions.md
  → corpus_to_astgrep.py               → outputs/defense/astgrep/rules/*.yaml
                                        → outputs/defense/astgrep/sgconfig.yml
  → scaffold_generator.py              → outputs/defense/scaffolds/{topology}/
  → diff_risk_classifier.py            → outputs/defense/diff_risk_model.json
  → checklist_library_builder.py       → outputs/defense/pr-checklists/checklist_library.yaml
```

## Rules per Tool

### copilot_instructions_generator.py
- For each invariant with confidence: high or medium: generate one instruction block.
- Instruction format: { rule_id, instruction_text (imperative, max 2 sentences),
  negative_example_pattern (optional), positive_example_pattern (optional) }
- Bundle into a single copilot-instructions.md with GH Copilot frontmatter.
- Do not include instructions derived from doctrine_reject findings without
  explicit labeling as `doctrine_violation_pattern`.

### corpus_to_astgrep.py
- For each rule_id with occurrence_count >= 2: generate one ast-grep rule YAML.
- Rule format: id, language, rule (pattern or regex), message, severity, note.
- Severity mapping: critical finding → error, high → warning, medium → info.
- Generate sgconfig.yml listing all rule file paths.
- Do not generate rules for rule_ids without a deterministic code pattern.
  Label those as `pattern_unknown` and skip.

### scaffold_generator.py
- For each active adapter (github-actions, python-uv, node-npm, polyglot):
  generate a project scaffold directory.
- Scaffold must include: pyproject.toml or package.json, .github/workflows/ci.yml,
  AGENTS.md (injected with generated invariants), .pre-commit-config.yaml.
- Scaffold ci.yml must include all fixes for known rule_ids in the topology.
- Do not generate a scaffold for an adapter with no corpus evidence.

### diff_risk_classifier.py
- Produce a JSON model mapping file path patterns to risk scores.
- Risk score derived from: how often that path pattern appeared in findings,
  effort_score of associated rule_ids.
- Output: diff_risk_model.json. Used by LSP to highlight high-risk files on open.

### checklist_library_builder.py
- For each topology class: generate a PR checklist block.
- Checklist item format: [ ] {check_text} (rule_id: {id})
- Bundle into checklist_library.yaml keyed by topology.
- Include a `universal` checklist block for items that apply to all topologies.

## Leverage Gate

Before publishing any defense output, score against L9-Leverage.yaml.
Minimum publish score: 4.0. Scaffolds must score >= 4.5 (they are reused
across all future projects — higher bar).
