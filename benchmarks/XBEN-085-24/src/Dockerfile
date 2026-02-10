FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir flask gunicorn pyyaml

# Copy application files
COPY app.py .
COPY templates templates/
COPY static static/
COPY config.yaml .

ARG FLAG

# Write the flag to a protected file that only the admin dashboard can read
RUN mkdir -p /app/data && \
    echo "$FLAG" > /app/data/api_key.txt && \
    chmod 600 /app/data/api_key.txt

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--access-logfile", "-", "app:app"]
