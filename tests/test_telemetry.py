from datetime import date

from src.optimizer import UserConstraints
from src.telemetry import build_chat_event, log_event, score_response_quality


def test_score_response_quality_detects_completeness_and_actionable():
    response = (
        "Take Friday 2026-04-03 off and you'll get 4 days off. "
        "Use 1 leave day with a strong ratio."
    )
    scores = score_response_quality(response)
    assert scores.completeness == 2
    assert scores.actionable >= 1
    assert scores.total >= 4


def test_score_response_quality_flags_excluded_dates_in_adherence():
    response = "Take leave on 2026-12-24 for a longer break."
    constraints = UserConstraints(
        max_leave_days=5,
        min_total_days_off=4,
        max_window_days=10,
        excluded_leave_dates={date(2026, 12, 24)},
    )
    scores = score_response_quality(response, constraints)
    assert scores.constraint_adherence < 2


def test_build_chat_event_and_log_event(tmp_path):
    constraints = UserConstraints(max_leave_days=4, min_total_days_off=5, max_window_days=12)
    event = build_chat_event(
        session_id="test-session",
        prompt="Help me around Easter",
        response="Take Friday 2026-04-03 off and get 4 days off with 1 leave day.",
        latency_ms=321,
        history_count_sent=4,
        has_holidays_data=True,
        year_selected=2026,
        tool_called=False,
        planner_constraints=constraints,
    )
    output_file = tmp_path / "events.csv"
    log_event(event, output_file)
    assert output_file.exists()
    content = output_file.read_text()
    assert "latency_ms" in content
    assert "event_id" in content
    assert "session_id" in content
    assert "test-session" in content
    assert "321" in content
