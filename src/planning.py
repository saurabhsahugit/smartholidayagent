from __future__ import annotations

from datetime import date, datetime

from src.optimizer import HolidayOptimizer, LeavePlan, UserConstraints

MONTH_NAME_TO_NUMBER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def build_constraints(
    max_leave_days: int,
    min_total_days_off: int,
    max_window_days: int,
    preferred_month_labels: list[str] | None = None,
    excluded_leave_dates: list[date] | None = None,
) -> UserConstraints:
    preferred_months = {
        MONTH_NAME_TO_NUMBER[label] for label in (preferred_month_labels or [])
    }
    return UserConstraints(
        max_leave_days=max_leave_days,
        min_total_days_off=min_total_days_off,
        preferred_months=preferred_months,
        excluded_leave_dates=set(excluded_leave_dates or []),
        max_window_days=max_window_days,
    )


def generate_ranked_plans(
    holidays_data: list[dict],
    year: int,
    constraints: UserConstraints,
    top_n: int = 3,
) -> list[LeavePlan]:
    optimizer = HolidayOptimizer(holidays_data, year)
    return optimizer.optimize(constraints=constraints, top_n=top_n)


def format_plan_dates(days: tuple[date, ...]) -> str:
    if not days:
        return "None"
    return ", ".join(day.strftime("%a %d %b") for day in days)


def format_plan_summary(plan: LeavePlan) -> dict[str, str]:
    holiday_labels = [day.strftime("%a %d %b %Y") for day in sorted(plan.holiday_dates)]
    return {
        "date_range": (
            f"{plan.start_date.strftime('%a %d %b %Y')} to "
            f"{plan.end_date.strftime('%a %d %b %Y')}"
        ),
        "leave_dates": format_plan_dates(plan.leave_dates),
        "holiday_dates": ", ".join(holiday_labels) if holiday_labels else "None",
        "weekend_count": str(len(plan.weekend_dates)),
        "total_days_off": str(plan.total_days_off),
        "leave_days_used": str(plan.leave_days_used),
        "efficiency_ratio": f"{plan.efficiency_ratio:.2f}",
    }


def parse_holiday_date(holiday: dict) -> date:
    return datetime.strptime(holiday["date"], "%Y-%m-%d").date()
