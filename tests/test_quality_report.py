from quality_report import summarize_telemetry


def test_summarize_telemetry_empty_file_path(tmp_path):
    summary = summarize_telemetry(tmp_path / "missing.csv")
    assert summary["events"] == 0
    assert summary["median_latency_ms"] == 0
    assert summary["p95_latency_ms"] == 0


def test_summarize_telemetry_computes_metrics(tmp_path):
    telemetry_file = tmp_path / "events.csv"
    telemetry_file.write_text(
        "latency_ms,q_total\n100,4\n200,6\n300,2\n", encoding="utf-8"
    )

    summary = summarize_telemetry(telemetry_file)

    assert summary["events"] == 3
    assert summary["median_latency_ms"] == 200
    assert summary["p95_latency_ms"] == 200
    assert summary["avg_q_total"] == 4.0
