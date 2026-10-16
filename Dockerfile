# Production Multi-Stage Dockerfile for OJAS Cybersecurity CTF
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Initialize and seed database if not present
RUN python -c "from models.db import init_database; init_database(reset=False, seed=True)"

EXPOSE 5000

# Run production server using Waitress or Gunicorn
CMD ["python", "run_production.py"]
