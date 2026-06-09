FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install runtime deps only (no test deps)
RUN uv pip install --system --no-cache \
    "fastapi>=0.115,<1.0" \
    "uvicorn[standard]>=0.30,<1.0" \
    "pydantic-settings>=2.0,<3.0"

# Copy source (volume mount overrides this in dev via compose)
COPY services/api/src ./services/api/src/

ENV PYTHONPATH=/app/services/api/src
WORKDIR /app/services/api
EXPOSE 8000

# Dev: reload enabled; remove --reload for production
CMD ["uvicorn", "nairi_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--reload"]
