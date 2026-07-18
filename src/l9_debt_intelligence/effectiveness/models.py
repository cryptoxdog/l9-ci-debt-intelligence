from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Outcome:
    event_id: str
    producer_id: str
    producer_contract: str
    pack_id: str
    pack_version: str
    canonical_rule_id: str
    surface: str
    outcome_class: str
    observation_scope: str
    observed_at: str
    finding_id: str | None
    repository_pseudonym: str | None
    snapshot_identity: str | None
    document_identity: str | None
    policy_mode: str | None
    latency_ms: int | None
    effort_minutes: int | None
    limitations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "l9.effectiveness-outcome/v1",
            "event_id": self.event_id,
            "producer_id": self.producer_id,
            "producer_contract": self.producer_contract,
            "pack_id": self.pack_id,
            "pack_version": self.pack_version,
            "canonical_rule_id": self.canonical_rule_id,
            "surface": self.surface,
            "outcome_class": self.outcome_class,
            "observation_scope": self.observation_scope,
            "observed_at": self.observed_at,
            "finding_id": self.finding_id,
            "repository_pseudonym": self.repository_pseudonym,
            "snapshot_identity": self.snapshot_identity,
            "document_identity": self.document_identity,
            "policy_mode": self.policy_mode,
            "latency_ms": self.latency_ms,
            "effort_minutes": self.effort_minutes,
            "limitations": list(self.limitations),
        }
