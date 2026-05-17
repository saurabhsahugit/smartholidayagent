# Week 1 Demo Script: Core AI Feature

This script proves the Week 1 goal: reliable core AI behavior with basic quality gates.

## Preconditions

- `OPENAI_API_KEY` is set in your environment.
- Dependencies installed (`pip install -r requirements.txt`).

## Demo steps (5 minutes)

1. **Show CI + local guardrails**
   - Open `.github/workflows/ci.yml` and explain Black/isort/pytest checks.
   - Run `make ci` locally.

2. **Show fallback behavior when key is missing**
   - Start app without `OPENAI_API_KEY`.
   - Enter a chat prompt and show warning fallback text.

3. **Show core AI happy path**
   - Set `OPENAI_API_KEY` and restart app.
   - Click **Load Holidays**.
   - Ask: "What is the best strategy around Easter this year?"
   - Show response includes concrete dates and leave strategy.

4. **Show missing data behavior**
   - Clear chat and do not load holidays.
   - Ask date-specific question.
   - Show the assistant asks user to load holiday data first.

## Success criteria

- End-to-end AI flow works with key + holiday context.
- Fallback paths are clear and user-safe when dependencies/context are missing.
