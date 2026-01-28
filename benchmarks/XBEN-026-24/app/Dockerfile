FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask gunicorn

# Create directory structure for configuration files
RUN mkdir -p /opt/configsync/configs \
    /opt/configsync/production \
    /opt/configsync/development \
    /etc/configsync-secret \
    /var/backups

# Copy application code
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/

# Create sample configuration files in each environment
RUN echo "# Base nginx configuration\nserver {\n    listen 80;\n    server_name localhost;\n}" > /opt/configsync/configs/nginx.conf && \
    echo "# Base application config\napp_name=configsync\nlog_level=info" > /opt/configsync/configs/app.conf && \
    echo "# Production database config\nhost=db.prod.internal\nport=5432" > /opt/configsync/production/database.conf && \
    echo "# Production secrets - DO NOT SHARE\napi_key=prod-api-key-12345" > /opt/configsync/production/secrets.conf && \
    echo "# Development config\ndebug=true\nlog_level=debug" > /opt/configsync/development/app.conf && \
    echo "# Dev database\nhost=localhost\nport=5432" > /opt/configsync/development/database.conf

# Create entrypoint script for runtime flag injection
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
