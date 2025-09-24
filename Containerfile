# ===== Build stage =====
FROM python:3.12-slim AS build-env

# Set working directory
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Create virtual environment
RUN python -m venv .venv \
    && .venv/bin/python -m ensurepip \
    && .venv/bin/pip install --upgrade pip \
    && .venv/bin/pip install --no-cache-dir -r requirements.txt

# ===== Runtime stage =====
FROM python:3.12-slim
WORKDIR /app

# Copy virtual environment from build stage
COPY --from=build-env /app/.venv /app/.venv

# Copy the application code
COPY main.py .

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "main.py"]