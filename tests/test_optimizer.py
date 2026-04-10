from datetime import date

from src.optimizer import (
    ConstraintHandler,
    EfficiencyCalculator,
    HolidayOptimizer,
    StrategyRanker,
    UserConstraints,
)


def sample_holidays_2026():
    return [
        {"title": "Good Friday", "date": "2026-04-03", "notes": "", "bunting": True},
        {
            "title": "Easter Monday",
            "date": "2026-04-06",
            "notes": "",
            "bunting": True,
        },
        {
            "title": "Early May bank holiday",
            "date": "2026-05-04",
            "notes": "",
            "bunting": True,
        },
        {
            "title": "Christmas Day",
            "date": "2026-12-25",
            "notes": "",
            "bunting": True,
        },
        {
            "title": "Boxing Day (substitute day)",
            "date": "2026-12-28",
            "notes": "",
            "bunting": True,
        },
    ]


def test_efficiency_calculator():
    assert EfficiencyCalculator.calculate_ratio(11, 4) == 2.75
    assert EfficiencyCalculator.calculate_ratio(9, 3) == 3.0


def test_optimizer_returns_ranked_plans():
    optimizer = HolidayOptimizer(sample_holidays_2026(), 2026)

    plans = optimizer.optimize(
        UserConstraints(max_leave_days=3, min_total_days_off=4, max_window_days=10),
        top_n=3,
    )

    assert len(plans) == 3
    assert plans[0].efficiency_ratio >= plans[1].efficiency_ratio
    assert any(date(2026, 4, 3) in plan.holiday_dates for plan in plans)


def test_optimizer_finds_easter_bridge():
    optimizer = HolidayOptimizer(sample_holidays_2026(), 2026)

    plans = optimizer.optimize(
        UserConstraints(max_leave_days=2, min_total_days_off=5, max_window_days=7),
        top_n=5,
    )

    easter_plan = next(
        (
            plan
            for plan in plans
            if plan.start_date == date(2026, 4, 3) and plan.end_date == date(2026, 4, 7)
        ),
        None,
    )

    assert easter_plan is not None
    assert easter_plan.leave_days_used == 1
    assert easter_plan.total_days_off == 5


def test_constraint_handler_respects_preferred_months_and_exclusions():
    optimizer = HolidayOptimizer(sample_holidays_2026(), 2026)

    plans = optimizer.optimize(
        UserConstraints(
            max_leave_days=2,
            min_total_days_off=4,
            preferred_months={12},
            excluded_leave_dates={date(2026, 12, 24)},
            max_window_days=7,
        ),
        top_n=5,
    )

    assert all(all(leave.month == 12 for leave in plan.leave_dates) for plan in plans)
    assert all(date(2026, 12, 24) not in plan.leave_dates for plan in plans)


def test_strategy_ranker_prefers_higher_ratio_then_longer_break():
    optimizer = HolidayOptimizer(sample_holidays_2026(), 2026)

    plans = optimizer.optimize(
        UserConstraints(max_leave_days=3, min_total_days_off=4, max_window_days=10),
        top_n=10,
    )
    ranked = StrategyRanker.rank(plans, top_n=2)

    assert ranked[0].efficiency_ratio >= ranked[1].efficiency_ratio
    if ranked[0].efficiency_ratio == ranked[1].efficiency_ratio:
        assert ranked[0].total_days_off >= ranked[1].total_days_off


def test_constraint_handler_rejects_large_leave_requests():
    optimizer = HolidayOptimizer(sample_holidays_2026(), 2026)
    plan = optimizer._build_plan(date(2026, 4, 1), date(2026, 4, 7))

    assert not ConstraintHandler.is_valid(
        plan,
        UserConstraints(max_leave_days=2, min_total_days_off=4, max_window_days=7),
    )
