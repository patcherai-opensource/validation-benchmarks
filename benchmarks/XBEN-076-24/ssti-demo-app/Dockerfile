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

# Create application directories
RUN mkdir -p /app/storage /app/templates /app/user_templates

# Set up flag from environment variable (for K8s compatibility)
# Flag is stored in a location only accessible via exploitation
ARG FLAG
ENV FLAG_VALUE=${FLAG}
RUN mkdir -p /app/config && \
    echo "${FLAG}" > /app/config/secret_key.txt && \
    chmod 644 /app/config/secret_key.txt

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
