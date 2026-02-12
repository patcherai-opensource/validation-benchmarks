FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health checks
RUN apt-get update -y && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Plant flag in a protected location (only accessible via OS command execution)
ARG FLAG
RUN mkdir -p /etc/flavor && \
    echo "${FLAG}" > /etc/flavor/.secret_key && \
    chmod 644 /etc/flavor/.secret_key

# Create pages directory
RUN mkdir -p /var/www/pages

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
