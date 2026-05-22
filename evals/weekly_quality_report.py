from __future__ import annotations

import sys
from pathlib import Path

from evals import run_quality_eval, summarize_results
from quality_report import summarize_telemetry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    telemetry = summarize_telemetry(Path("data/telemetry_events.csv"))
    eval_results = run_quality_eval(Path("data/eval_prompts_responses.csv"))
    eval_summary = summarize_results(eval_results)

    print("=== Weekly Quality Snapshot ===")
    print(f"telemetry_events={telemetry['events']}")
    print(f"median_latency_ms={telemetry['median_latency_ms']}")
    print(f"p95_latency_ms={telemetry['p95_latency_ms']}")
    print(f"avg_q_total={telemetry['avg_q_total']}")
    print(f"eval_cases={eval_summary['total_cases']}")
    print(f"eval_passed={eval_summary['passed_cases']}")
    print(f"eval_pass_rate={eval_summary['pass_rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
