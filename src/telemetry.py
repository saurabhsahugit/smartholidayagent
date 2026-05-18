from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.optimizer import UserConstraints

TELEMETRY_PATH = Path("data/telemetry_events.csv")
TELEMETRY_FIELDS = [
    "event_id",
    "timestamp_utc",
    "session_id",
    "year_selected",
    "region",
    "has_holidays_data",
    "history_count_sent",
    "prompt_len_chars",
    "response_len_chars",
    "tool_called",
    "tool_name",
    "latency_ms",
    "error_type",
    "q_completeness",
    "q_constraint_adherence",
    "q_actionable",
    "q_total",
]


@dataclass(frozen=True)
class QualityScores:
    completeness: int
    constraint_adherence: int
    actionable: int

    @property
    def total(self) -> int:
        return self.completeness + self.constraint_adherence + self.actionable


def score_response_quality(
    response_text: str,
    constraints: UserConstraints | None = None,
) -> QualityScores:
    text = response_text.lower()

    date_pattern = re.compile(
        r"\b\d{4}-\d{2}-\d{2}\b|\b(mon|tue|wed|thu|fri|sat|sun)\b", re.IGNORECASE
    )
    completeness = 1 if date_pattern.search(text) else 0
    if any(token in text for token in ["leave", "days off", "ratio"]):
        completeness += 1

    adherence = 2
    if constraints and constraints.max_leave_days:
        suggested_leave = _extract_leave_days(text)
        if suggested_leave is not None and suggested_leave > constraints.max_leave_days:
            adherence -= 1
    if constraints and constraints.excluded_leave_dates:
        for excluded_date in constraints.excluded_leave_dates:
            if excluded_date.isoformat() in text:
                adherence -= 1
                break
    adherence = max(0, adherence)

    actionable = 1 if any(token in text for token in ["take", "book", "plan"]) else 0
    if "load holidays" in text or "take" in text:
        actionable += 1

    return QualityScores(
        completeness=min(completeness, 2),
        constraint_adherence=min(adherence, 2),
        actionable=min(actionable, 2),
    )


def build_chat_event(
    *,
    session_id: str,
    prompt: str,
    response: str,
    latency_ms: int,
    history_count_sent: int,
    has_holidays_data: bool,
    year_selected: int,
    tool_called: bool,
    planner_constraints: UserConstraints | None = None,
    region: str = "england-and-wales",
    tool_name: str = "",
    error_type: str = "",
) -> dict:
    quality = score_response_quality(response, planner_constraints)
    return {
        "event_id": str(uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "year_selected": year_selected,
        "region": region,
        "has_holidays_data": has_holidays_data,
        "history_count_sent": history_count_sent,
        "prompt_len_chars": len(prompt),
        "response_len_chars": len(response),
        "tool_called": tool_called,
        "tool_name": tool_name,
        "latency_ms": latency_ms,
        "error_type": error_type,
        "q_completeness": quality.completeness,
        "q_constraint_adherence": quality.constraint_adherence,
        "q_actionable": quality.actionable,
        "q_total": quality.total,
    }


def log_event(event: dict, file_path: Path = TELEMETRY_PATH) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        _migrate_legacy_csv_if_needed(file_path)

    with file_path.open("a", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=TELEMETRY_FIELDS)
        if file_path.stat().st_size == 0:
            writer.writeheader()
        row = {field: event.get(field, "") for field in TELEMETRY_FIELDS}
        writer.writerow(row)


def _extract_leave_days(text: str) -> int | None:
    matches = re.findall(r"(\d+)\s+leave day", text)
    if not matches:
        return None
    return int(matches[0])


def _migrate_legacy_csv_if_needed(file_path: Path) -> None:
    with file_path.open("r", newline="", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        existing_fields = reader.fieldnames or []
        rows = list(reader)

    if all(field in existing_fields for field in TELEMETRY_FIELDS):
        return

    with file_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=TELEMETRY_FIELDS)
        writer.writeheader()
        for old_row in rows:
            migrated_row = {field: old_row.get(field, "") for field in TELEMETRY_FIELDS}
            writer.writerow(migrated_row)
