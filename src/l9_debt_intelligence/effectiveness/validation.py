from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .errors import OutcomeValidationError
from .models import Outcome

SURFACE_OUTCOMES = {
    "CI": {
        "prevented_before_merge",
        "detected_in_CI",
        "escaped_detection",
        "rule_not_evaluated",
        "evaluation_incomplete",
    },
    "LSP": {
        "diagnostic_shown",
        "diagnostic_accepted",
        "diagnostic_dismissed",
        "confirmed_false_positive",
        "quick_fix_applied",
        "quick_fix_reverted",
        "rule_not_evaluated",
        "evaluation_incomplete",
    },
    "repair": {
        "repair_succeeded",
        "repair_failed",
        "repair_partial",
        "repair_rolled_back",
        "outcome_unknown",
    },
}


class OutcomeValidator:
    def __init__(self, schema_path: Path) -> None:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    def validate(self, event: dict[str, Any]) -> Outcome:
        errors = sorted(
            self.validator.iter_errors(event),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            message = "; ".join(
                f"{'/'.join(map(str, error.absolute_path))}: {error.message}"
                for error in errors
            )
            raise OutcomeValidationError(message)
        surface = event["surface"]
        outcome_class = event["outcome_class"]
        if outcome_class not in SURFACE_OUTCOMES[surface]:
            raise OutcomeValidationError(
                f"{outcome_class} is not valid for surface {surface}"
            )
        return Outcome(
            event_id=event["event_id"],
            producer_id=event["producer_id"],
            producer_contract=event["producer_contract"],
            pack_id=event["pack_id"],
            pack_version=event["pack_version"],
            canonical_rule_id=event["canonical_rule_id"],
            surface=surface,
            outcome_class=outcome_class,
            observation_scope=event["observation_scope"],
            observed_at=event["observed_at"],
            finding_id=event.get("finding_id"),
            repository_pseudonym=event.get("repository_pseudonym"),
            snapshot_identity=event.get("snapshot_identity"),
            document_identity=event.get("document_identity"),
            policy_mode=event.get("policy_mode"),
            latency_ms=event.get("latency_ms"),
            effort_minutes=event.get("effort_minutes"),
            limitations=tuple(sorted(set(event.get("limitations", [])))),
        )
