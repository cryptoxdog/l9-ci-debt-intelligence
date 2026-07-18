from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RedactionAssessment:
    safe: bool
    reason: str | None
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IngestionResult:
    schema_version: str
    status: str
    event_id: str
    event_hash: str
    record_id: str | None
    quarantine_id: str | None
    observation_id: str
    ledger_sequence: int
    limitations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "event_id": self.event_id,
            "event_hash": self.event_hash,
            "record_id": self.record_id,
            "quarantine_id": self.quarantine_id,
            "observation_id": self.observation_id,
            "ledger_sequence": self.ledger_sequence,
            "limitations": list(self.limitations),
        }
