# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install uv

# Copy project files
COPY pyproject.toml .

# Generate requirements.txt using uv (mocking the export mainly since we don't have a lock file yet)
# In a real flow with uv, we might use `uv pip install` directly, but let's stick to standard pip for the image
# to avoid complex multi-stage uv setups unless requested.
# However, the user asked for `uv`.
# Let's try to use uv to create a venv in the builder stage.

ENV VIRTUAL_ENV=/app/.venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies into the virtual environment
COPY pyproject.toml .
# We don't have a lock file yet, so we install from pyproject.toml
# Note: uv pip install -r pyproject.toml is not direct.
# We'll rely on pip for now to keep it simple and robust without a lock file, 
# OR we can use `uv pip install .` if we copy the source info.
# Use standard pip to install build dependencies if needed.
# Let's stick to the user's request: "Install uv, compile dependencies."

# Since we don't have a lockfile, we'll just install directly.
# Since we don't have a lockfile, we'll compile to requirements.txt first
# This avoids shell syntax issues with <(...) in /bin/sh
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt || \
    pip install .

# Stage 2: Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

# Install system dependencies for Playwright
# and basic tools
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder? Or just install? 
# The prompt says: "builder: Install uv, compile dependencies. runtime: python:3.11-slim. Install playwright dependencies".
# We'll copy the installed packages or re-install. 
# A cleaner way given we started with `uv` in builder:
# Let's just install in runtime to be safe and simple, efficiently.

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install Playwright browsers (chromium only to save space/time, or all)
RUN playwright install-deps
RUN playwright install chromium

# Copy application code
COPY src/ /app/src/
COPY pyproject.toml /app/

# Environment variables
ENV PYTHONPATH=/app/src
ENV APP_ENV=production

# Expose port (7860 is standard for Hugging Face Spaces)
EXPOSE 7860

# Install Gunicorn for production process management
RUN pip install gunicorn

# Command: Use Gunicorn with Uvicorn worker class
# Bind to $PORT if set, otherwise default to 7860 (Hugging Face default)
CMD ["sh", "-c", "gunicorn mugeshbabu_agents.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-7860}"]
