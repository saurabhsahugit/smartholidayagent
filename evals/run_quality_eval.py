from __future__ import annotations

import sys
from pathlib import Path

from evals import run_quality_eval, summarize_results

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    eval_file = Path("data/eval_prompts_responses.csv")
    results = run_quality_eval(eval_file)
    summary = summarize_results(results)

    print("=== Quality Eval Results ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(
            f"{status} | {r.case_id} | q_total={r.q_total} "
            f"(min={r.min_q_total}) | c={r.q_completeness}, "
            f"a={r.q_constraint_adherence}, act={r.q_actionable}"
        )

    print("---")
    print(f"total_cases={summary['total_cases']}")
    print(f"passed_cases={summary['passed_cases']}")
    print(f"pass_rate={summary['pass_rate']}")
    print(f"avg_q_total={summary['avg_q_total']}")

    return 0 if summary["passed_cases"] == summary["total_cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
