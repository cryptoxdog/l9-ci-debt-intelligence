from __future__ import annotations

import re
from typing import Any

from .models import RedactionAssessment

SENSITIVE_KEY = re.compile(
    r"(?:"
    r"authorization|"
    r"password|"
    r"passwd|"
    r"secret|"
    r"token|"
    r"api[_-]?key|"
    r"private[_-]?key|"
    r"client[_-]?secret"
    r")",
    re.IGNORECASE,
)
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
ABSOLUTE_PATH = re.compile(
    r"(?:"
    r"(?<![A-Za-z0-9_.-])/(?:home|Users|var|tmp|private|opt)/[^\s]+"
    r"|"
    r"(?<![A-Za-z0-9_.-])[A-Za-z]:\\[^\s]+"
    r")"
)


def inspect_value(
    value: Any,
    *,
    path: tuple[str, ...] = (),
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if SENSITIVE_KEY.search(key_text):
                findings.append(f"sensitive-key:{'.'.join(path + (key_text,))}")
            findings.extend(
                inspect_value(
                    child,
                    path=path + (key_text,),
                )
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                inspect_value(
                    child,
                    path=path + (str(index),),
                )
            )
    elif isinstance(value, str):
        for pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                findings.append(f"sensitive-value:{'.'.join(path)}")
                break
        if ABSOLUTE_PATH.search(value):
            findings.append(f"absolute-path:{'.'.join(path)}")
    return findings


def assess_redaction(event: dict[str, Any]) -> RedactionAssessment:
    status = event.get("redaction_status")
    if status == "quarantine_required":
        return RedactionAssessment(
            safe=False,
            reason="redaction_required",
            limitations=("producer marked the event as requiring quarantine",),
        )
    findings = sorted(set(inspect_value(event.get("payload", {}))))
    if findings:
        return RedactionAssessment(
            safe=False,
            reason="sensitive_content",
            limitations=tuple(findings),
        )
    return RedactionAssessment(
        safe=True,
        reason=None,
        limitations=(),
    )
