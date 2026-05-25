# Smart Holiday Agent — AI Engineering Case Study

## Problem framing
UK holiday planning is often manual and error-prone. Users need recommendations that maximize consecutive days off while minimizing leave-day usage.

## Architecture decision
I intentionally split responsibilities:
- **Deterministic optimizer** (`src/optimizer.py`) computes ranked leave options with explicit constraints.
- **LLM layer** (`src/llm_handler.py`) explains and personalizes recommendations in natural language.

This keeps optimization reliable while still providing a conversational AI experience.

## Evaluation strategy
The project evaluates both system performance and AI usefulness.

### Operational metrics
Captured in telemetry events:
- `latency_ms`
- `tool_called` / `tool_name`
- request/response size and context metadata

### Quality signals
Rule-based quality scoring in `src/telemetry.py`:
- `q_completeness`
- `q_constraint_adherence`
- `q_actionable`
- `q_total`

## Validation strategy
### Unit and integration coverage
Existing tests validate optimizer logic, planning adapters, holidays data loading, LLM tool-call flow, and telemetry event logging.

### Behavior-level checks
Behavior tests validate AI-response properties relevant to user value:
- explicit dates in recommendations
- leave constraints respected
- excluded dates not recommended
- actionable guidance quality


### What behavior tests prove today
The current behavior tests are **evaluation-contract tests** for the scoring rubric, not full model-judgment tests. They prove the quality-scoring logic is stable and catches regressions in how responses are graded (dates, constraints, excluded dates, and actionability).

### What they do not prove
They do not prove that a live model will always produce high-quality responses in production.

### Replay-eval layer (next-level proof implemented)
A lightweight replay evaluation set now exists at `data/eval_prompts_responses.csv`. A runner (`evals/run_quality_eval.py`) periodically scores these prompt/response traces via the same production rubric and fails when any case drops below its minimum score threshold.

## Key trade-offs
- **Determinism vs flexibility:** deterministic ranking improves reproducibility; LLM adds flexible explanations.
- **Speed vs depth:** keeping tool-calls bounded improves latency, but limits long-form exploration.
- **Simple rules vs semantic judges:** rule-based quality scoring is cheap and transparent but not fully semantic.

## Outcome signal for interviews
This project demonstrates a practical AI engineering workflow:
1. build a working AI feature,
2. instrument measurable quality,
3. gate behavior in CI,
4. explain trade-offs with evidence.
