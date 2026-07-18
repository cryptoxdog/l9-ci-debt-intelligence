from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ProducerCompatibilityError, SDKCompatibilityError


@dataclass(frozen=True)
class ProducerContract:
    producer_id: str
    event_classes: frozenset[str]
    contract_versions: frozenset[str]
    required_sdk_contract: str


class CompatibilityRegistry:
    def __init__(
        self,
        producers: dict[str, ProducerContract],
        *,
        unknown_producer_behavior: str,
        unknown_contract_behavior: str,
        incompatible_sdk_behavior: str,
    ) -> None:
        self._producers = producers
        self.unknown_producer_behavior = unknown_producer_behavior
        self.unknown_contract_behavior = unknown_contract_behavior
        self.incompatible_sdk_behavior = incompatible_sdk_behavior

    @classmethod
    def load(cls, path: Path) -> CompatibilityRegistry:
        document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        if document.get("schema") != "l9.producer-compatibility/v1":
            raise ProducerCompatibilityError(
                "unsupported producer compatibility registry schema"
            )
        raw_producers = document.get("producers")
        if not isinstance(raw_producers, dict):
            raise ProducerCompatibilityError(
                "producer registry must contain a producers object"
            )
        producers: dict[str, ProducerContract] = {}
        for producer_id, value in raw_producers.items():
            if not isinstance(value, dict):
                raise ProducerCompatibilityError(
                    f"producer {producer_id!r} must be an object"
                )
            event_classes = value.get("event_classes")
            contract_versions = value.get("contract_versions")
            sdk_contract = value.get("required_sdk_contract")
            if not isinstance(event_classes, list) or not all(
                isinstance(item, str) for item in event_classes
            ):
                raise ProducerCompatibilityError(
                    f"producer {producer_id!r} has invalid event classes"
                )
            if not isinstance(contract_versions, list) or not all(
                isinstance(item, str) for item in contract_versions
            ):
                raise ProducerCompatibilityError(
                    f"producer {producer_id!r} has invalid contracts"
                )
            if not isinstance(sdk_contract, str) or not sdk_contract:
                raise ProducerCompatibilityError(
                    f"producer {producer_id!r} has no SDK contract"
                )
            producers[producer_id] = ProducerContract(
                producer_id=producer_id,
                event_classes=frozenset(event_classes),
                contract_versions=frozenset(contract_versions),
                required_sdk_contract=sdk_contract,
            )
        return cls(
            producers,
            unknown_producer_behavior=str(
                document.get("unknown_producer_behavior", "quarantine")
            ),
            unknown_contract_behavior=str(
                document.get("unknown_contract_behavior", "quarantine")
            ),
            incompatible_sdk_behavior=str(
                document.get("incompatible_sdk_behavior", "quarantine")
            ),
        )

    def validate(
        self,
        *,
        producer_id: str,
        event_class: str,
        producer_contract: str,
        sdk_contract: str | None,
    ) -> ProducerContract:
        producer = self._producers.get(producer_id)
        if producer is None:
            raise ProducerCompatibilityError(f"unknown producer: {producer_id}")
        if event_class not in producer.event_classes:
            raise ProducerCompatibilityError(
                f"producer {producer_id!r} cannot emit event class {event_class!r}"
            )
        if producer_contract not in producer.contract_versions:
            raise ProducerCompatibilityError(
                f"unsupported producer contract: {producer_contract}"
            )
        if sdk_contract != producer.required_sdk_contract:
            raise SDKCompatibilityError(
                f"producer requires SDK contract "
                f"{producer.required_sdk_contract!r}, "
                f"received {sdk_contract!r}"
            )
        return producer
