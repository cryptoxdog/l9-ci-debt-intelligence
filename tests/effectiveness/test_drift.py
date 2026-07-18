from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from l9_debt_intelligence.effectiveness.drift import (
    compare_reports,
)


def report(
    report_id: str,
    *,
    false_positive: float,
    escape: float,
    prevention: float,
    latency: int,
) -> dict:
    return {
        "report_id": report_id,
        "pack_id": "pack_" + ("a" * 64),
        "observation_count": 100,
        "pack_metrics": {
            "prevention_ratio": prevention,
            "escape_ratio": escape,
            "false_positive_ratio": false_positive,
            "unknown_ratio": 0.0,
            "coverage_ratio": 1.0,
            "p95_latency_ms": latency,
        },
    }


class DriftTests(unittest.TestCase):
    def test_critical_false_positive_regression(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = root / "baseline.json"
            current = root / "current.json"
            baseline.write_text(
                json.dumps(
                    report(
                        "effect_" + ("b" * 64),
                        false_positive=0.01,
                        escape=0.01,
                        prevention=0.80,
                        latency=100,
                    )
                )
            )
            current.write_text(
                json.dumps(
                    report(
                        "effect_" + ("c" * 64),
                        false_positive=0.15,
                        escape=0.02,
                        prevention=0.75,
                        latency=110,
                    )
                )
            )
            comparison = compare_reports(
                baseline_path=baseline,
                current_path=current,
            )
            self.assertEqual(
                "critical_regression",
                comparison["regression_state"],
            )


if __name__ == "__main__":
    unittest.main()
