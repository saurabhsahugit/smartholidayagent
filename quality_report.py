from __future__ import annotations

import csv
from pathlib import Path


def summarize_telemetry(file_path: Path) -> dict[str, float | int]:
    if not file_path.exists():
        return {
            "events": 0,
            "median_latency_ms": 0,
            "p95_latency_ms": 0,
            "avg_q_total": 0.0,
        }

    with file_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    latencies = sorted(
        int(row.get("latency_ms", 0) or 0)
        for row in rows
        if str(row.get("latency_ms", "")).strip()
    )
    q_totals = [
        int(row.get("q_total", 0) or 0)
        for row in rows
        if str(row.get("q_total", "")).strip()
    ]

    return {
        "events": len(rows),
        "median_latency_ms": _median(latencies),
        "p95_latency_ms": _percentile(latencies, 0.95),
        "avg_q_total": round((sum(q_totals) / len(q_totals)) if q_totals else 0.0, 2),
    }


def _median(values: list[int]) -> int:
    if not values:
        return 0
    mid = len(values) // 2
    if len(values) % 2 == 1:
        return values[mid]
    return int((values[mid - 1] + values[mid]) / 2)


def _percentile(values: list[int], quantile: float) -> int:
    if not values:
        return 0
    idx = int((len(values) - 1) * quantile)
    return values[idx]
