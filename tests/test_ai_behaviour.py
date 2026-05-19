from datetime import date

from src.optimizer import UserConstraints
from src.telemetry import score_response_quality


def test_behavior_response_mentions_concrete_dates_when_data_exists():
    response = (
        "For Easter, take leave on 2026-04-07. "
        "Good Friday is on 2026-04-03 and Easter Monday is 2026-04-06."
    )

    scores = score_response_quality(response)

    assert scores.completeness >= 1


def test_behavior_respects_max_leave_days_constraint():
    response = "Take 5 leave days for this plan to get 10 days off."
    constraints = UserConstraints(
        max_leave_days=3,
        min_total_days_off=5,
        max_window_days=14,
    )

    scores = score_response_quality(response, constraints)

    assert scores.constraint_adherence == 1


def test_behavior_flags_excluded_dates_as_adherence_risk():
    response = "Take leave on 2026-12-24 and 2026-12-29 for a long break."
    constraints = UserConstraints(
        max_leave_days=5,
        min_total_days_off=5,
        max_window_days=14,
        excluded_leave_dates={date(2026, 12, 24)},
    )

    scores = score_response_quality(response, constraints)

    assert scores.constraint_adherence == 1


def test_behavior_actionable_guidance_scores_higher():
    actionable_response = (
        "Book Friday 2026-05-22 as leave and plan a 4-day weekend around it."
    )
    non_actionable_response = "There are some holidays in May and June."

    actionable = score_response_quality(actionable_response)
    non_actionable = score_response_quality(non_actionable_response)

    assert actionable.actionable > non_actionable.actionable
