# Smart Holiday Agent — 4-Week AI Leadership Roadmap

This roadmap is tuned to maximize **AI leadership signal** in 4 weeks: not just software process maturity, but your ability to design, evaluate, and communicate AI decisions.

## Outcome to optimize for
By the end of Week 4, you should be able to clearly demonstrate:
- You built a working AI feature end-to-end.
- You instrumented and measured AI quality (not only latency).
- You validated AI behavior with practical tests, including lightweight semantic checks.
- You can explain trade-offs and decision quality in a concise case study.

---

## Week 1 — Basic CI + working AI feature (core functionality)

### Goal
Establish minimum engineering reliability while ensuring the core AI experience is solid and demoable.

### Deliverables
- Basic CI checks on pull requests.
- Reliable AI feature flow (user prompt → model response → strategy recommendation) with clear fallback behavior.

### Tasks
- [ ] Add basic CI workflow (`.github/workflows/ci.yml`) with:
  - `black --check .`
  - `isort --check-only .`
  - `pytest -q`
- [ ] Verify and harden core AI feature path:
  - prompt handling
  - holiday context injection
  - recommendation output format
  - safe fallback when `OPENAI_API_KEY` or holiday data is missing
- [ ] Add one short demo script in docs for the core AI flow

### Leadership signal to discuss
- “I prioritized a shippable AI core, then wrapped it in lightweight reliability checks.”

### Done when
- A reviewer can run the app and see a consistent end-to-end AI experience.

---

## Week 2 — AI telemetry + quality signals (beyond latency)

### Goal
Move from “it works” to “we can measure how well it works.”

### Deliverables
- AI telemetry collection for interaction and outcome metrics.
- Dashboard/report showing quality signals, not just performance timing.

### Tasks
- [ ] Add event logging (CSV/SQLite) for:
  - request timestamp
  - prompt type/category
  - response latency
  - tool call usage
- [ ] Add **quality signals**:
  - recommendation completeness (dates, leave days, total days off present)
  - policy adherence (stays in UK holiday scope / constraints)
  - actionable score (can user act on this response directly?)
- [ ] Add quick dashboard or report with weekly trend lines for both latency + quality

### Leadership signal to discuss
- “I defined measurable AI quality criteria aligned to user value, not just model speed.”

### Done when
- You can show one chart for speed and one chart for usefulness/quality.

---

## Week 3 — Integration + AI behavior tests + lightweight semantic validation

### Goal
Prove reliability of the full AI workflow and catch subtle reasoning drift.

### Deliverables
- Integration tests for major user journeys.
- AI behavior test suite with lightweight semantic checks.

### Tasks
- [ ] Add integration tests for:
  - load holidays
  - generate ranked plans
  - LLM/tool-call response path using deterministic mock client
- [ ] Add AI behavior tests for expected response properties:
  - mentions concrete dates when data exists
  - respects constraints (max leave days, excluded dates)
  - provides clear recommendation rationale
- [ ] Add lightweight semantic reasoning validation (rule-based rubric):
  - response claims are consistent with returned plan metrics
  - no contradiction between suggested leave and excluded dates
  - rationale aligns with efficiency calculation

### Leadership signal to discuss
- “I tested AI behavior quality, not just function outputs, with pragmatic semantic checks.”

### Done when
- CI catches both code regressions and basic reasoning-quality regressions.

---

## Week 4 — Package + case study (AI decisions and trade-offs)

### Goal
Convert implementation into a strong portfolio artifact focused on AI decision-making quality.

### Deliverables
- Packaged demo-ready project setup.
- Case study centered on AI decisions, evaluation approach, and trade-offs.

### Tasks
- [ ] Package runtime for reproducibility (container or scripted setup)
- [ ] Create `docs/CASE_STUDY.md` covering:
  - problem framing
  - AI architecture decisions (deterministic optimizer + LLM explanation)
  - telemetry and quality signal design
  - test strategy for behavior + semantic validation
  - trade-offs (speed vs quality, determinism vs flexibility, cost vs depth)
- [ ] Prepare 5-minute demo flow:
  - live AI interaction
  - telemetry/quality dashboard snapshot
  - one reasoning-validation test example

### Leadership signal to discuss
- “I can justify AI design choices with evidence, constraints, and measured outcomes.”

### Done when
- You can confidently walk through decisions, metrics, and trade-offs in interview format.

---

## Weekly tracker (Friday check-in)

- CI pass rate (%)
- Median and p95 latency (ms)
- AI response quality score (completeness + adherence + actionable)
- AI behavior test pass rate (%)
- One documented AI improvement decision per week

---

## Scope guardrails (keep this achievable)

In this 4-week plan, avoid major platform expansion. Focus on:
- Core AI value and reliability
- AI quality observability
- Practical AI evaluation
- Clear trade-off storytelling
