# Use a small, secure base
FROM python:3.12-slim

# Prevent Python from writing .pyc files & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Make Pip faster & safer in containers
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system deps only if you compile packages (uncomment if needed)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser

WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Cloud Run listens on 8080 by convention
EXPOSE 8080

# Drop privileges
USER appuser

# Use gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:main"]
