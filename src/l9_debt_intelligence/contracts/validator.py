from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import sha256_document
from .errors import (
    ProducerCompatibilityError,
    SchemaValidationError,
    SDKCompatibilityError,
)
from .registry import CompatibilityRegistry


@dataclass(frozen=True)
class ValidationResult:
    schema_version: str
    status: str
    event_id: str
    producer_id: str
    event_class: str
    event_hash: str
    quarantine_reason: str | None
    limitations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "event_id": self.event_id,
            "producer_id": self.producer_id,
            "event_class": self.event_class,
            "event_hash": self.event_hash,
            "quarantine_reason": self.quarantine_reason,
            "limitations": list(self.limitations),
        }


class EventValidator:
    def __init__(
        self,
        *,
        event_schema: Path,
        compatibility_registry: Path,
    ) -> None:
        schema = json.loads(event_schema.read_text(encoding="utf-8"))
        self._validator = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )
        self._registry = CompatibilityRegistry.load(compatibility_registry)

    def validate(self, event: dict[str, Any]) -> ValidationResult:
        errors = sorted(
            self._validator.iter_errors(event),
            key=lambda error: tuple(str(part) for part in error.path),
        )
        event_hash = sha256_document(event)
        event_id = str(event.get("event_id", "unknown"))
        producer_id = str(event.get("producer_id", "unknown"))
        event_class = str(event.get("event_class", "unknown"))
        limitations = tuple(event.get("limitations", []))
        if errors:
            message = "; ".join(
                f"{'/'.join(str(part) for part in error.path) or '<root>'}: "
                f"{error.message}"
                for error in errors
            )
            raise SchemaValidationError(message)
        try:
            self._registry.validate(
                producer_id=event["producer_id"],
                event_class=event["event_class"],
                producer_contract=event["producer_contract"],
                sdk_contract=event.get("sdk_contract"),
            )
        except (ProducerCompatibilityError, SDKCompatibilityError) as error:
            return ValidationResult(
                schema_version="l9.intelligence-validation-result/v1",
                status="quarantined",
                event_id=event_id,
                producer_id=producer_id,
                event_class=event_class,
                event_hash=event_hash,
                quarantine_reason=type(error).__name__,
                limitations=limitations + (str(error),),
            )
        if event["redaction_status"] == "quarantine_required":
            return ValidationResult(
                schema_version="l9.intelligence-validation-result/v1",
                status="quarantined",
                event_id=event_id,
                producer_id=producer_id,
                event_class=event_class,
                event_hash=event_hash,
                quarantine_reason="redaction_required",
                limitations=limitations,
            )
        return ValidationResult(
            schema_version="l9.intelligence-validation-result/v1",
            status="accepted",
            event_id=event_id,
            producer_id=producer_id,
            event_class=event_class,
            event_hash=event_hash,
            quarantine_reason=None,
            limitations=limitations,
        )
