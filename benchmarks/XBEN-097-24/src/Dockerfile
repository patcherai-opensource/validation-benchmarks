FROM python:3.11-slim

ARG FLAG="FLAG{placeholder}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/sitemonitor

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

# Application data directory
RUN mkdir -p /opt/appdata/monitors

# Application configuration
RUN echo '{"datastore": "/opt/appdata", "secret_file": "/opt/appdata/.secret_token", "max_monitors": 100, "check_interval": 300}' > /opt/appdata/config.json
RUN chmod 644 /opt/appdata/config.json

# Store application secret token used for internal API auth
RUN echo "${FLAG}" > /opt/appdata/.secret_token
RUN chmod 644 /opt/appdata/.secret_token

# Clean up build arg from environment
RUN unset FLAG || true

# Runtime user
RUN useradd -m appuser && chown -R appuser:appuser /opt/sitemonitor /opt/appdata
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "-m", "app.main"]
