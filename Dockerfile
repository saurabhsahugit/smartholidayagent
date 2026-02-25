FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY tests /app/tests

# Toggle dev deps
ARG INSTALL_DEV=false
RUN pip install --no-cache-dir -U pip && \
    if [ "$INSTALL_DEV" = "true" ]; then \
      pip install --no-cache-dir -e ".[dev]"; \
    else \
      pip install --no-cache-dir -e "."; \
    fi

EXPOSE 8000
CMD ["uvicorn", "smartholidayagent.main:app", "--host", "0.0.0.0", "--port", "8000"]