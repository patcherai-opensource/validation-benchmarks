FROM python:3.11-slim

ARG FLAG

WORKDIR /opt/platform

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create application structure
RUN mkdir -p /opt/platform/data/storage \
    && mkdir -p /opt/platform/data/secrets \
    && mkdir -p /opt/platform/data/registry

# Plant the flag in a secrets file (only accessible via vulnerability)
RUN echo "${FLAG}" > /opt/platform/data/secrets/credentials.txt \
    && chmod 600 /opt/platform/data/secrets/credentials.txt

# Add sample data to make environment realistic
RUN echo '{"db_engine": "sqlite", "backend_uri": "sqlite:///opt/platform/data/tracker.db", "storage_root": "/opt/platform/data/storage", "registry_dir": "/opt/platform/data/registry"}' \
    > /opt/platform/data/config.json

COPY app.py .

# Health check
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
