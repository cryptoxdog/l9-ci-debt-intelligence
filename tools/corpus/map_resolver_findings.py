"""Map resolver-schema findings into corpus-schema records.

The resolver (l9-ci-debt-resolver) emits findings shaped by
`schemas/ci_debt_finding.schema.json` (failure_type / root_cause / outcome).
The intelligence corpus expects `schemas/corpus.schema.json`
(classification / rule_id / action / tenant_id / language / ci_system).

This tool performs a deterministic, lossless field mapping so resolver
findings survive `ingest_findings.py` schema validation instead of being
silently dropped. Every corpus field traces to a resolver field or a
documented default. No finding data is invented.

Mapping rules:
  finding_id     <- finding_id
  repo           <- repo
  rule_id        <- failure_type (resolver category id)
  tenant_id      <- repo owner (repo before '/'), else repo, else "unknown"
  classification <- outcome: "unknown"/absent -> "unknown"; else "valid_current"
  action         <- outcome: "repaired" -> "patch"; else "not_patched"
  source         <- "gha_log" (resolver findings derive from GitHub Actions logs)
  ci_system      <- existing ci_system, else default (GHA constructs: job_name/run_id)
  language       <- existing language, else default "unknown"
  pr             <- pr_number when present (enables normalize dedup/sort)
All original resolver fields are preserved for provenance; the resolver's
`source` constant is retained as `resolver_source` to avoid enum collision.
"""
from __future__ import annotations

import json
from pathlib import Path

import typer

app = typer.Typer()

_UNKNOWN = "unknown"


def _classification(outcome: str | None) -> str:
    if not outcome or outcome == "unknown":
        return "unknown"
    return "valid_current"


def _action(outcome: str | None) -> str:
    return "patch" if outcome == "repaired" else "not_patched"


def _tenant_id(repo: str) -> str:
    if not repo:
        return _UNKNOWN
    return repo.split("/", 1)[0] if "/" in repo else repo


def map_record(r: dict, *, ci_system: str, language: str) -> dict:
    """Return a corpus-schema record derived from one resolver finding."""
    mapped = dict(r)
    mapped["resolver_source"] = mapped.pop("source", "l9-ci-debt-resolver")
    mapped["finding_id"] = r["finding_id"]
    mapped["repo"] = r["repo"]
    mapped["rule_id"] = r.get("failure_type") or "UNKNOWN"
    mapped["classification"] = _classification(r.get("outcome"))
    mapped["action"] = _action(r.get("outcome"))
    mapped["tenant_id"] = _tenant_id(r.get("repo", ""))
    mapped["ci_system"] = r.get("ci_system") or ci_system
    mapped["language"] = r.get("language") or language
    mapped["source"] = "gha_log"
    if r.get("pr_number") is not None:
        mapped["pr"] = r["pr_number"]
    return mapped


@app.command()
def map_findings(
    findings_jsonl: Path = typer.Argument(..., help="Resolver CI_DEBT_FINDINGS.jsonl"),
    output_path: Path = typer.Option(Path("/tmp/corpus_ready.jsonl"), help="Corpus-format JSONL output"),
    ci_system: str = typer.Option("github-actions", help="Default ci_system when absent"),
    language: str = typer.Option(_UNKNOWN, help="Default language when absent"),
) -> None:
    """Convert resolver findings JSONL to corpus-format JSONL."""
    mapped: list[dict] = []
    for lineno, raw in enumerate(findings_jsonl.read_text().splitlines(), start=1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(f"line {lineno}: JSON decode error — {exc}") from exc
        mapped.append(map_record(record, ci_system=ci_system, language=language))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as fh:
        for r in mapped:
            fh.write(json.dumps(r) + "\n")

    typer.echo(f"Mapped {len(mapped)} resolver findings → {output_path}")


if __name__ == "__main__":
    app()
