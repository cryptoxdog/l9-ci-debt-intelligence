from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    recurrence: float
    scope_breadth: float
    effort: float
    repair_success: float
    false_positive_safety: float

    @property
    def total(self) -> float:
        value = (
            self.recurrence * 0.30
            + self.scope_breadth * 0.20
            + self.effort * 0.15
            + self.repair_success * 0.15
            + self.false_positive_safety * 0.20
        )
        return round(min(5.0, max(0.0, value)), 6)

    def as_dict(self) -> dict[str, float]:
        return {
            "recurrence": self.recurrence,
            "scope_breadth": self.scope_breadth,
            "effort": self.effort,
            "repair_success": self.repair_success,
            "false_positive_safety": self.false_positive_safety,
        }


def capped_ratio(value: int | float | None, target: float) -> float:
    if value is None or target <= 0:
        return 0.0
    return round(min(5.0, max(0.0, float(value) / target * 5)), 6)


def calculate_score(
    *,
    occurrence_count: int,
    distinct_scope_count: int,
    mean_effort_minutes: float | None,
    repair_success_ratio: float | None,
    false_positive_ratio: float | None,
) -> Score:
    return Score(
        recurrence=capped_ratio(occurrence_count, 10),
        scope_breadth=capped_ratio(distinct_scope_count, 5),
        effort=capped_ratio(mean_effort_minutes, 120),
        repair_success=(
            round(repair_success_ratio * 5, 6)
            if repair_success_ratio is not None
            else 0.0
        ),
        false_positive_safety=(
            round((1.0 - false_positive_ratio) * 5, 6)
            if false_positive_ratio is not None
            else 0.0
        ),
    )


def candidate_state(score: float) -> str:
    if score >= 4.0:
        return "promotion_eligible"
    if score >= 3.0:
        return "compiled_candidate"
    return "deferred"
