<!-- L9_META
l9_schema: 1
parent: l9-ci-debt-intelligence
layer: reference
role: deployment_sequencing
tags: [sequencing, build-order, dependency, cross-repo]
owner: igor_beylin
status: active
version: 1.0.0
updated: 2026-07-02
/L9_META -->

# Deployment Sequencing

## Three-Repo Build Order

The three repos must be built and activated in strict sequence:

```
1. l9-ci-debt-resolver       ← must be green CI and emitting corpus first
2. l9-ci-debt-intelligence   ← this repo; requires resolver corpus as input
3. l9-ci-debt-lsp            ← requires compiled rules from this repo
```

Do not activate l9-ci-debt-intelligence until at least one full resolver run
has produced a non-empty `PR_REMEDIATION_FINDINGS.jsonl`.

Do not activate l9-ci-debt-lsp until at least one full intelligence pipeline
run has produced non-empty `outputs/defense/astgrep/rules/` and
`outputs/defense/copilot/copilot-instructions.md`.

## Cross-Repo Dependency Invariants

- This repo MUST NOT import from or call l9-ci-debt-resolver at runtime.
  Corpus is exchanged via file artifacts only.
- This repo MUST NOT import from or call l9-ci-debt-lsp at runtime.
  Compiled rules are exchanged via file artifacts only.
- The one-way flow is: resolver emits → intelligence consumes → LSP consumes.
  No reverse calls. No circular dependencies.

## CI Trigger Rules

- `corpus-update.yml` triggers on: push to resolver repo's reports/ dir (via
  repository_dispatch), or manual workflow_dispatch with corpus_path input.
- `publish-astgrep-pack.yml` triggers on: completion of corpus-update.yml with
  status success, or manual workflow_dispatch.
- `publish-scaffolds.yml` triggers on: completion of corpus-update.yml with
  status success, or manual workflow_dispatch.
- `validate-intelligence-outputs.yml` triggers on: every push to main.

## Minimum Viable First Run

For the initial corpus run before resolver has accumulated findings:

1. Use the synthetic fixture corpus at `tests/fixtures/synthetic_corpus.jsonl`
   (seeded with the 4 known root-cause findings from the resolver session).
2. Run offense + defense lanes against the fixture.
3. Validate outputs.
4. Mark all fixture-derived outputs with `source: fixture` in their headers.
5. Replace with live corpus artifacts on first real resolver run.
