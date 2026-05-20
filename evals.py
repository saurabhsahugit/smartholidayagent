from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.optimizer import UserConstraints
from src.telemetry import score_response_quality


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt: str
    response: str
    max_leave_days: int
    excluded_leave_dates: list[str]
    min_q_total: int


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    q_total: int
    q_completeness: int
    q_constraint_adherence: int
    q_actionable: int
    min_q_total: int
    passed: bool


def load_eval_cases(file_path: Path) -> list[EvalCase]:
    with file_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cases = []
    for row in rows:
        excluded_dates = [
            d.strip()
            for d in row.get("excluded_leave_dates", "").split(";")
            if d.strip()
        ]
        cases.append(
            EvalCase(
                case_id=row["case_id"],
                prompt=row["prompt"],
                response=row["response"],
                max_leave_days=int(row["max_leave_days"]),
                excluded_leave_dates=excluded_dates,
                min_q_total=int(row["min_q_total"]),
            )
        )
    return cases


def run_quality_eval(file_path: Path) -> list[EvalResult]:
    results: list[EvalResult] = []
    for case in load_eval_cases(file_path):
        constraints = UserConstraints(
            max_leave_days=case.max_leave_days,
            min_total_days_off=1,
            max_window_days=31,
            excluded_leave_dates={
                _parse_iso_date(d) for d in case.excluded_leave_dates
            },
        )
        scores = score_response_quality(case.response, constraints)
        results.append(
            EvalResult(
                case_id=case.case_id,
                q_total=scores.total,
                q_completeness=scores.completeness,
                q_constraint_adherence=scores.constraint_adherence,
                q_actionable=scores.actionable,
                min_q_total=case.min_q_total,
                passed=scores.total >= case.min_q_total,
            )
        )
    return results


def summarize_results(results: list[EvalResult]) -> dict[str, float | int]:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = (passed / total) if total else 0.0
    avg_q_total = (sum(r.q_total for r in results) / total) if total else 0.0
    return {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": round(pass_rate, 4),
        "avg_q_total": round(avg_q_total, 2),
    }


def _parse_iso_date(value: str):
    from datetime import datetime

    return datetime.strptime(value, "%Y-%m-%d").date()
