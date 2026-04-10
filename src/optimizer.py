from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable


@dataclass(frozen=True)
class UserConstraints:
    max_leave_days: int = 5
    min_total_days_off: int = 1
    preferred_months: set[int] = field(default_factory=set)
    excluded_leave_dates: set[date] = field(default_factory=set)
    max_window_days: int = 18


@dataclass(frozen=True)
class LeavePlan:
    start_date: date
    end_date: date
    leave_dates: tuple[date, ...]
    holiday_dates: tuple[date, ...]
    weekend_dates: tuple[date, ...]
    total_days_off: int
    leave_days_used: int
    efficiency_ratio: float

    @property
    def consecutive_days_off(self) -> int:
        return self.total_days_off

    def summary(self) -> str:
        return (
            f"{self.total_days_off} days off using {self.leave_days_used} leave days "
            f"(ratio {self.efficiency_ratio:.2f}) from "
            f"{self.start_date.isoformat()} to {self.end_date.isoformat()}"
        )


class EfficiencyCalculator:
    @staticmethod
    def calculate_ratio(total_days_off: int, leave_days_used: int) -> float:
        if leave_days_used == 0:
            return float(total_days_off)
        return round(total_days_off / leave_days_used, 2)


class ConstraintHandler:
    @staticmethod
    def is_valid(plan: LeavePlan, constraints: UserConstraints) -> bool:
        if plan.leave_days_used > constraints.max_leave_days:
            return False
        if plan.total_days_off < constraints.min_total_days_off:
            return False
        if plan.total_days_off > constraints.max_window_days:
            return False
        if constraints.preferred_months:
            months_in_plan = {
                day.month for day in plan.leave_dates or (plan.start_date,)
            }
            if not months_in_plan.issubset(constraints.preferred_months):
                return False
        if constraints.excluded_leave_dates.intersection(plan.leave_dates):
            return False
        return True


class StrategyRanker:
    @staticmethod
    def rank(plans: Iterable[LeavePlan], top_n: int = 3) -> list[LeavePlan]:
        ranked = sorted(
            plans,
            key=lambda plan: (
                plan.efficiency_ratio,
                plan.total_days_off,
                -plan.leave_days_used,
                -plan.start_date.toordinal(),
            ),
            reverse=True,
        )
        return ranked[:top_n]


class HolidayOptimizer:
    def __init__(self, holidays_data: list[dict], year: int):
        self.year = year
        self.holiday_dates = self._parse_holiday_dates(holidays_data, year)

    def optimize(
        self, constraints: UserConstraints | None = None, top_n: int = 3
    ) -> list[LeavePlan]:
        constraints = constraints or UserConstraints()
        plans: dict[tuple[date, ...], LeavePlan] = {}
        current = date(self.year, 1, 1)
        final_day = date(self.year, 12, 31)

        while current <= final_day:
            max_end = min(
                current + timedelta(days=constraints.max_window_days - 1), final_day
            )
            interval_end = current

            while interval_end <= max_end:
                plan = self._build_plan(current, interval_end)
                if (
                    plan.holiday_dates
                    and ConstraintHandler.is_valid(plan, constraints)
                    and plan.leave_dates
                ):
                    signature = plan.leave_dates
                    existing = plans.get(signature)
                    if existing is None or self._is_better_plan(plan, existing):
                        plans[signature] = plan
                interval_end += timedelta(days=1)

            current += timedelta(days=1)

        return StrategyRanker.rank(plans.values(), top_n=top_n)

    def _build_plan(self, start_date: date, end_date: date) -> LeavePlan:
        leave_dates: list[date] = []
        holiday_dates: list[date] = []
        weekend_dates: list[date] = []
        cursor = start_date

        while cursor <= end_date:
            if cursor in self.holiday_dates:
                holiday_dates.append(cursor)
            elif cursor.weekday() >= 5:
                weekend_dates.append(cursor)
            else:
                leave_dates.append(cursor)
            cursor += timedelta(days=1)

        total_days_off = (end_date - start_date).days + 1
        leave_days_used = len(leave_dates)
        efficiency_ratio = EfficiencyCalculator.calculate_ratio(
            total_days_off, leave_days_used
        )

        return LeavePlan(
            start_date=start_date,
            end_date=end_date,
            leave_dates=tuple(leave_dates),
            holiday_dates=tuple(holiday_dates),
            weekend_dates=tuple(weekend_dates),
            total_days_off=total_days_off,
            leave_days_used=leave_days_used,
            efficiency_ratio=efficiency_ratio,
        )

    @staticmethod
    def _is_better_plan(candidate: LeavePlan, current: LeavePlan) -> bool:
        return (
            candidate.efficiency_ratio,
            candidate.total_days_off,
            -candidate.leave_days_used,
            -candidate.start_date.toordinal(),
        ) > (
            current.efficiency_ratio,
            current.total_days_off,
            -current.leave_days_used,
            -current.start_date.toordinal(),
        )

    @staticmethod
    def _parse_holiday_dates(holidays_data: list[dict], year: int) -> set[date]:
        holiday_dates: set[date] = set()
        for holiday in holidays_data:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
            if holiday_date.year == year:
                holiday_dates.add(holiday_date)
        return holiday_dates
