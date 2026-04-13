# --- Stage 1: Builder ---
FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for uv and Python
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies only (leverage Docker layer caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-editable

# --- Stage 2: Runtime ---
FROM python:3.12-slim-bookworm

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Create logging directory and set permissions
RUN mkdir -p /var/log/app && chown appuser:appgroup /var/log/app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY copilot_orchestrator/ /app/copilot_orchestrator/

# Ensure the appuser owns the app directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the API port
EXPOSE 8000

# Start the application with uvicorn
CMD ["uvicorn", "copilot_orchestrator.presentation.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
