# Use a lightweight base image
FROM python:3.10-slim

# Set environment variables for efficient execution
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory inside the container
WORKDIR /app

# Copy necessary files
COPY pyproject.toml poetry.lock ./
COPY api/ /app/api/
COPY src/ /app/src/
COPY config/ /app/config/
COPY scripts/ /app/scripts/
COPY security/ /app/security/

# Install Poetry for dependency management
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Expose API port
EXPOSE 8000

# Default command to run FastAPI application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
