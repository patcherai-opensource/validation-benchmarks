FROM python:3.11-slim

ARG FLAG
RUN test -n "$FLAG" || (echo "FLAG build arg is required" && exit 1)

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Plant the flag in a realistic location (only accessible via file: protocol path traversal)
RUN echo "$FLAG" > /datastore/secret-api-key.txt 2>/dev/null || \
    (mkdir -p /datastore && echo "$FLAG" > /datastore/secret-api-key.txt)
RUN chmod 644 /datastore/secret-api-key.txt

# Copy application
COPY changedetectionio/ /app/changedetectionio/

# Set up data directory for watches
RUN mkdir -p /datastore/watches

# Production environment - do not expose debug info
ENV FLASK_ENV=production
ENV HIDE_REFERRER=true
ENV NOTIFICATION_URLS=""
ENV ALLOW_FILE_URI=false

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "changedetectionio.flask_app:app"]
