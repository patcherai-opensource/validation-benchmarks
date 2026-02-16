FROM python:3.11-slim

ARG FLAG="FLAG_PLACEHOLDER"

WORKDIR /opt/conductor

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY auth.py .
COPY content_backend.py .
COPY server.py .
COPY templates/ templates/
COPY static/ static/

# Setup content directories and sample files
COPY setup_content.sh /tmp/setup_content.sh
RUN chmod +x /tmp/setup_content.sh && /tmp/setup_content.sh && rm /tmp/setup_content.sh

# Generate master signing key for node authentication
RUN mkdir -p /etc/conductor && \
    echo "${FLAG}" > /etc/conductor/master.key && \
    chmod 644 /etc/conductor/master.key

# Create log directory
RUN mkdir -p /var/log/conductor

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "120", "server:app"]
