# Use lightweight Python 3.11 image (stable and widely supported)
FROM python:3.11.8-slim

# Copy uv binary for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Set working directory inside container
WORKDIR /code

# Add uv-created virtual environment to PATH
ENV PATH="/code/.venv/bin:$PATH"

# Copy dependency files first (layer caching)
COPY pyproject.toml .python-version uv.lock ./

# Install dependencies exactly as locked
RUN uv sync --locked

# Copy application code
COPY ingest_data.py .

# Entry point: always run this script
ENTRYPOINT ["python", "ingest_data.py"]

# Default arguments (empty by default, can be overridden)
CMD []
