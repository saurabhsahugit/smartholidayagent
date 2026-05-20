from pathlib import Path

from evals import load_eval_cases, run_quality_eval, summarize_results


def test_load_eval_cases_reads_csv():
    cases = load_eval_cases(Path("data/eval_prompts_responses.csv"))
    assert len(cases) >= 3
    assert cases[0].case_id


def test_run_quality_eval_returns_structured_results():
    results = run_quality_eval(Path("data/eval_prompts_responses.csv"))
    assert len(results) >= 3
    assert all(hasattr(r, "q_total") for r in results)


def test_summarize_results_has_expected_keys():
    results = run_quality_eval(Path("data/eval_prompts_responses.csv"))
    summary = summarize_results(results)
    assert set(summary.keys()) == {
        "total_cases",
        "passed_cases",
        "pass_rate",
        "avg_q_total",
    }
