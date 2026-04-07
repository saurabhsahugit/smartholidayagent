**Smart Holiday Agent**

AI-powered system that helps UK users optimise holiday planning by maximising time off while minimising leave usage.

**Problem**

Planning holidays around UK public holidays is inefficient and manual.
Users struggle to identify optimal leave patterns that maximise consecutive days off.

**Solution**

An AI-powered assistant that:

- Analyses UK public holidays
- Calculates optimal leave combinations
- Uses LLMs to generate personalised holiday plans
- Provides ranked recommendations based on efficiency
- System Overview

**High-level flow:**

1. User inputs preferences (dates, flexibility, location)
2. System retrieves UK public holiday data
3. Optimization logic generates candidate leave plans
4. LLM refines and presents results in natural language

**Architecture**
- Frontend: Streamlit
- Backend: Python
- LLM: OpenAI API
- Data: UK public holiday dataset

**Logic:**
Rule-based optimisation for leave/holiday planning
LLM for explanation and user interaction

**Key Design Decisions**
- Used LLM for explanation, not core optimisation
- Kept optimisation deterministic for reliability
- API-based LLM approach to reduce complexity
- Modular design to allow future model replacement

**Trade-offs**
- API vs custom model: faster to build, less control
- Cost vs response quality
- Deterministic logic vs generative flexibility

**Limitations**
- No real-time travel pricing
- Dependent on static holiday data
- LLM responses may vary in quality

*Future Improvements*
- Integrate flight and hotel APIs
- Add user preferences and memory
- Introduce cost-aware recommendations
