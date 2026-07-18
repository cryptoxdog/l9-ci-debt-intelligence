from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .models import PartitionPlan, SnapshotRecord

SAFE_COMPONENT = re.compile(r"[^A-Za-z0-9._-]+")


def safe_component(value: str) -> str:
    normalized = SAFE_COMPONENT.sub("_", value).strip("._")
    if not normalized:
        return "unknown"
    return normalized[:120]


def plan_partitions(
    records: tuple[SnapshotRecord, ...],
) -> tuple[PartitionPlan, ...]:
    groups: dict[
        tuple[str, str],
        list[SnapshotRecord],
    ] = defaultdict(list)
    for record in records:
        groups[(record.event_class, record.producer_id)].append(record)
    plans: list[PartitionPlan] = []
    for event_class, producer_id in sorted(groups):
        partition_records = tuple(
            sorted(
                groups[(event_class, producer_id)],
                key=lambda value: value.record_id,
            )
        )
        relative_path = (
            Path("partitions")
            / f"event_class={safe_component(event_class)}"
            / f"producer_id={safe_component(producer_id)}"
            / "records.parquet"
        )
        plans.append(
            PartitionPlan(
                event_class=event_class,
                producer_id=producer_id,
                relative_path=relative_path,
                records=partition_records,
            )
        )
    return tuple(plans)
