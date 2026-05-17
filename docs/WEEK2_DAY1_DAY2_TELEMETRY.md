# Week 2 — Day 1 & Day 2: Telemetry Schema + Instrumentation Plan

This document defines the **official telemetry schema first (Day 1)** and then the **minimum instrumentation work (Day 2)**.

## Day 1: Telemetry schema (before coding)

### Purpose
Capture one event per AI response so we can measure both performance and usefulness.

### Event name
`ai_chat_response`

### Required fields
| Field | Type | Example | Why it matters |
|---|---|---|---|
| `event_id` | string (uuid4) | `e9...` | unique row identity |
| `timestamp_utc` | ISO-8601 string | `2026-05-07T12:34:56Z` | trend analysis over time |
| `session_id` | string | `streamlit-session-hash` | per-session debugging |
| `year_selected` | int | `2026` | response context |
| `region` | string | `england-and-wales` | scope tracking |
| `has_holidays_data` | bool | `true` | input completeness |
| `history_count_sent` | int | `8` | prompt size control |
| `prompt_len_chars` | int | `420` | cost/latency proxy |
| `response_len_chars` | int | `610` | output verbosity proxy |
| `tool_called` | bool | `true` | routing/agent behavior |
| `tool_name` | string \| null | `get_ranked_holiday_strategies` | tool-level insights |
| `latency_ms` | int | `1430` | speed metric |
| `error_type` | string \| null | `timeout` | reliability tracking |
| `q_completeness` | int (0-2) | `2` | quality signal |
| `q_constraint_adherence` | int (0-2) | `1` | quality signal |
| `q_actionability` | int (0-2) | `2` | quality signal |
| `q_total` | int (0-6) | `5` | aggregate quality |

### Quality rubric (v1)
- `q_completeness`:
  - +1 includes concrete date-like content.
  - +1 includes leave recommendation and/or quantified outcome.
- `q_constraint_adherence`:
  - Start at 2.
  - -1 if response appears to exceed `max_leave_days`.
  - -1 if response suggests excluded leave dates.
- `q_actionability`:
  - +1 explicit action language (`take`, `book`, `plan`).
  - +1 clear next step (including `load holidays` fallback guidance).

## Day 2: Instrumentation tasks

### Scope
Only instrument the existing chat path. No dashboard expansion on Day 2.

### Implementation checklist
1. Measure latency around `create_chat_completion`.
2. Build one event object using the Day 1 schema.
3. Persist events to `data/telemetry_events.csv`.
4. Ensure missing/failed calls still log an event with `error_type`.
5. Add tests for schema shape and CSV writing.

### Acceptance criteria
- Every successful AI response writes one telemetry row.
- Failed AI calls write one telemetry row with `error_type` populated.
- CSV header contains all required Day 1 fields in a stable order.
