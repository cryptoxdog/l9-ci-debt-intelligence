# Agent Instructions
This repository owns historical corpus learning and prevention-artifact
compilation.
Before modifying the authoritative implementation:
1. Read `.l9/architecture.yaml`.
2. Read `.l9/ownership.yaml`.
3. Read `.l9/sdk-schema-registry.json`.
4. Read `.l9/producer-compatibility.json`.
5. Preserve producer lineage.
6. Represent missing data explicitly as unknown.
7. Reference SDK schemas; never reproduce them.
8. Use correction or retraction events; never silently rewrite history.
9. Keep source repository mutation out of this repository.
10. Run the complete Phase 1 contract suite.
The following are prohibited:
- repository patching;
- branch pushing;
- scanner-native parsing;
- SDK private imports;
- producer implementation imports;
- fabricated corpus fields;
- publishing unversioned prevention artifacts.
Legacy `tools/`, `adapters/`, `outputs/`, and root legacy schemas are
transitional and are not authoritative Phase 1 implementation packages.

## INTEL-P1 ingestion rules
- Normalize before calculating corpus identity.
- Never include arrival time in corpus record identity.
- Append every observation to the ledger.
- Store accepted records immutably.
- Quarantine suspected sensitive content.
- Never fabricate a sanitized payload.
- Treat duplicate delivery as an observation, not a new record.
- Treat identity collisions as quarantine events.
- Keep snapshot, analytics, and compiler dependencies out of ingestion.
## INTEL-P2 snapshot rules
- Verify the ingestion store before snapshot construction.
- Sort records by canonical record identity.
- Exclude build time and machine state from snapshot identity.
- Never overwrite an existing snapshot.
- Hash every partition.
- Preserve the source record set hash.
- Treat DuckDB as a rebuildable projection.
- Keep analytics metrics and rule compilation outside this phase.
- Never place source content, raw logs, secrets, or absolute paths in Parquet.
## INTEL-P3 analytical rules
- Read only verified immutable snapshots.
- Preserve the source snapshot identity in every report.
- Keep missing values explicitly unknown.
- Never convert missing effort to zero.
- Never infer success or failure from missing outcomes.
- Deduplicate fingerprints within a co-occurrence scope.
- Sort all report rows deterministically.
- Hash every analytical report.
- Do not generate rules, invariants, fixes, or defense packs in analytics.
## INTEL-P4 compiler rules
- Compile only from a verified INTEL-P3 analysis run.
- Preserve source snapshot and analysis-run lineage.
- Keep every generated output in candidate state.
- Never let unknown evidence increase a score.
- Never promote or enable blocking policy from this repository.
- Generate positive and negative regression fixtures.
- Fail compilation when regression fixtures fail.
- Sort candidates and artifacts deterministically.
- Keep signing, release publication, and retirement out of this phase.
## INTEL-P5 publication rules
- Publish only verified INTEL-P4 compiler output.
- Include only promotion-eligible candidates.
- Pin corpus snapshot, analysis run, compilation, compiler, taxonomy, and SDK
  contract versions.
- Build byte-reproducible archives.
- Sign the archive SHA-256 digest with an external Ed25519 private key.
- Never commit or package private keys.
- Publish minimal executable prevention data only.
- Never distribute corpus records, raw logs, source content, or repository
  identities.
- Require rollback metadata for shadow and stable publication.
- Never overwrite an existing pack version.
- Record retirement through append-only events.
- Never edit Core governance or activate blocking policy.
## INTEL-P6 effectiveness rules
- Accept only versioned canonical producer outcome events.
- Preserve pack, rule, finding, and producer lineage.
- Deduplicate repeated event delivery deterministically.
- Keep source content, raw logs, developer identities, and absolute paths out
  of effectiveness events.
- Treat missing and incomplete outcomes as unknown.
- Never infer PASS from `rule_not_evaluated`.
- Measure rule and pack coverage explicitly.
- Require minimum sample sizes before rollback or retirement recommendations.
- Compare compatible identities and metric definitions only.
- Keep recommendations advisory.
- Never mutate Core governance, activate LSP packs, delete releases, or execute
  automatic retirement.
