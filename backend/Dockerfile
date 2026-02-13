FROM python:3.14-slim

# Ensures console output is not buffered by Docker
ENV PYTHONUNBUFFERED=1

# Will not get prompted for input
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Update repos and update packages
RUN apt-get update -qq
RUN apt-get upgrade -yq

# Install apt-utils so debian will not complain about delaying configurations
RUN apt-get install -yq --no-install-recommends apt-utils

# Install system dependencies for PostgreSQL
RUN apt-get install -yq --no-install-recommends gcc python3-dev libpq-dev postgresql-client

# Upgrade pip and install uv
RUN pip install --no-cache-dir --upgrade pip

# Install uv
RUN pip install uv

# Copy dependency files first (for better layer caching)
COPY pyproject.toml uv.lock* ./

# Install Python dependencies
RUN uv sync --frozen || uv sync

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD uv run python manage.py migrate && uv run python manage.py runserver 0.0.0.0:8000
