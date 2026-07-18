from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LearningObservation:
    record_id: str
    producer_id: str
    event_class: str
    producer_contract: str
    occurrence_scope: str
    recurrence_fingerprint: str
    canonical_rule_id: str | None = None
    repository_identity: str | None = None
    component: str | None = None
    remediation_class: str | None = None
    effort_minutes: int | None = None
    validation_outcome: str | None = None
    false_positive_disposition: str | None = None
    pack_version: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "l9.learning-observation/v1",
            "record_id": self.record_id,
            "producer_id": self.producer_id,
            "event_class": self.event_class,
            "producer_contract": self.producer_contract,
            "occurrence_scope": self.occurrence_scope,
            "recurrence_fingerprint": self.recurrence_fingerprint,
            "canonical_rule_id": self.canonical_rule_id,
            "repository_identity": self.repository_identity,
            "component": self.component,
            "remediation_class": self.remediation_class,
            "effort_minutes": self.effort_minutes,
            "validation_outcome": self.validation_outcome,
            "false_positive_disposition": (self.false_positive_disposition),
            "pack_version": self.pack_version,
        }
