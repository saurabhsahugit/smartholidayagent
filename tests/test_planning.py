from datetime import date

from src.planning import build_constraints, format_plan_summary, generate_ranked_plans


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


def test_build_constraints_maps_month_labels_and_exclusions():
    constraints = build_constraints(
        max_leave_days=4,
        min_total_days_off=5,
        max_window_days=12,
        preferred_month_labels=["April", "December"],
        excluded_leave_dates=[date(2026, 12, 24)],
    )

    assert constraints.max_leave_days == 4
    assert constraints.min_total_days_off == 5
    assert constraints.max_window_days == 12
    assert constraints.preferred_months == {4, 12}
    assert constraints.excluded_leave_dates == {date(2026, 12, 24)}


def test_generate_ranked_plans_returns_ranked_options():
    constraints = build_constraints(
        max_leave_days=2,
        min_total_days_off=5,
        max_window_days=7,
        preferred_month_labels=["April"],
    )

    plans = generate_ranked_plans(sample_holidays_2026(), 2026, constraints, top_n=3)

    assert plans
    assert len(plans) <= 3
    assert all(all(day.month == 4 for day in plan.leave_dates) for plan in plans)


def test_format_plan_summary_returns_ui_friendly_strings():
    constraints = build_constraints(
        max_leave_days=2,
        min_total_days_off=5,
        max_window_days=7,
        preferred_month_labels=["April"],
    )
    plan = generate_ranked_plans(sample_holidays_2026(), 2026, constraints, top_n=1)[0]

    summary = format_plan_summary(plan)

    assert "2026" in summary["date_range"]
    assert summary["leave_days_used"].isdigit()
    assert summary["total_days_off"].isdigit()
    assert float(summary["efficiency_ratio"]) >= 1.0
