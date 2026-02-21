FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first for better layer caching
COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir .

# Copy source
COPY src /app/src

# Expose port used by uvicorn
EXPOSE 8000

# Run the app
CMD ["uvicorn", "smartholidayagent.main:app", "--host", "0.0.0.0", "--port", "8000"]