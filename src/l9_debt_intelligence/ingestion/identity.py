from __future__ import annotations

import hashlib
from typing import Any

from l9_debt_intelligence.contracts.canonical import canonical_json


def namespaced_hash(prefix: str, document: Any) -> str:
    digest = hashlib.sha256(canonical_json(document)).hexdigest()
    return f"{prefix}{digest}"


def record_id(
    *,
    producer_id: str,
    producer_contract: str,
    event_class: str,
    snapshot_or_run_id: str,
    payload_hash: str,
) -> str:
    return namespaced_hash(
        "cr_",
        {
            "event_class": event_class,
            "payload_hash": payload_hash,
            "producer_contract": producer_contract,
            "producer_id": producer_id,
            "snapshot_or_run_id": snapshot_or_run_id,
        },
    )


def quarantine_id(event_hash: str, reason: str) -> str:
    return namespaced_hash(
        "qr_",
        {
            "event_hash": event_hash,
            "reason": reason,
        },
    )


def observation_id(
    *,
    event_hash: str,
    observed_at: str,
    sequence: int,
) -> str:
    return namespaced_hash(
        "obs_",
        {
            "event_hash": event_hash,
            "observed_at": observed_at,
            "sequence": sequence,
        },
    )
