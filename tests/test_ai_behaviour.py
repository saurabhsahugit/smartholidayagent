from datetime import date

from src.optimizer import UserConstraints
from src.telemetry import score_response_quality


def test_quality_contract_scores_are_bounded():
    response = "Take leave on 2026-04-07 for 4 days off with a strong ratio."

    scores = score_response_quality(response)

    assert 0 <= scores.completeness <= 2
    assert 0 <= scores.constraint_adherence <= 2
    assert 0 <= scores.actionable <= 2
    assert 0 <= scores.total <= 6


def test_quality_contract_prefers_dated_recommendation_over_generic_text():
    generic_response = "There are bank holidays in spring and winter."
    dated_response = (
        "Take leave on 2026-04-07 after Easter Monday 2026-04-06 for 5 days off."
    )

    generic = score_response_quality(generic_response)
    dated = score_response_quality(dated_response)

    assert dated.completeness > generic.completeness


def test_quality_contract_penalizes_excess_leave_against_constraint():
    constraints = UserConstraints(
        max_leave_days=3,
        min_total_days_off=5,
        max_window_days=14,
    )

    within_budget = score_response_quality(
        "Take 2 leave days to create 6 days off.", constraints
    )
    over_budget = score_response_quality(
        "Take 5 leave days to create 10 days off.", constraints
    )

    assert over_budget.constraint_adherence < within_budget.constraint_adherence


def test_quality_contract_penalizes_excluded_leave_dates():
    constraints = UserConstraints(
        max_leave_days=5,
        min_total_days_off=5,
        max_window_days=14,
        excluded_leave_dates={date(2026, 12, 24)},
    )

    allowed = score_response_quality(
        "Take leave on 2026-12-29 to extend your break.", constraints
    )
    excluded = score_response_quality(
        "Take leave on 2026-12-24 and 2026-12-29 to extend your break.", constraints
    )

    assert excluded.constraint_adherence < allowed.constraint_adherence


def test_quality_contract_prefers_actionable_language():
    passive_response = "The public holidays are listed for the year."
    actionable_response = "Book Friday 2026-05-22 and plan a 4-day weekend around it."

    passive = score_response_quality(passive_response)
    actionable = score_response_quality(actionable_response)

    assert actionable.actionable > passive.actionable
