from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json
from l9_debt_intelligence.snapshots.hashing import (
    namespaced_document_hash,
    sha256_bytes,
)

from .models import Outcome


def outcome_identity(outcome: Outcome) -> str:
    return namespaced_document_hash(
        "outcome_",
        {
            "producer_id": outcome.producer_id,
            "producer_contract": outcome.producer_contract,
            "event_id": outcome.event_id,
            "pack_id": outcome.pack_id,
            "canonical_rule_id": outcome.canonical_rule_id,
            "observation_scope": outcome.observation_scope,
        },
    )


class OutcomeStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.records = self.root / "records"
        self.ledger = self.root / "ledger/outcomes.jsonl"

    def initialize(self) -> None:
        self.records.mkdir(parents=True, exist_ok=True)
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        self.ledger.touch(exist_ok=True)

    def ingest(self, outcome: Outcome) -> dict[str, Any]:
        self.initialize()
        identity = outcome_identity(outcome)
        destination = self.records / f"{identity}.json"
        document = {
            "outcome_id": identity,
            **outcome.as_dict(),
        }
        encoded = canonical_json(document) + b"\n"
        status = "accepted"
        if destination.exists():
            if destination.read_bytes() != encoded:
                raise RuntimeError(f"outcome identity collision: {identity}")
            status = "duplicate"
        else:
            descriptor = os.open(
                destination,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o644,
            )
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        observation = {
            "schema_version": "l9.effectiveness-ledger-entry/v1",
            "outcome_id": identity,
            "status": status,
            "event_id": outcome.event_id,
            "pack_id": outcome.pack_id,
            "canonical_rule_id": outcome.canonical_rule_id,
            "observed_at": outcome.observed_at,
            "document_sha256": sha256_bytes(canonical_json(document)),
        }
        with self.ledger.open("ab") as stream:
            stream.write(canonical_json(observation) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        return {
            "schema_version": "l9.effectiveness-ingestion-result/v1",
            "status": status,
            "outcome_id": identity,
            "pack_id": outcome.pack_id,
            "canonical_rule_id": outcome.canonical_rule_id,
        }

    def load(
        self,
        *,
        pack_id: str | None = None,
    ) -> tuple[dict[str, Any], ...]:
        self.initialize()
        records: list[dict[str, Any]] = []
        for path in sorted(self.records.glob("outcome_*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            if pack_id and value.get("pack_id") != pack_id:
                continue
            records.append(value)
        return tuple(
            sorted(
                records,
                key=lambda item: item["outcome_id"],
            )
        )
