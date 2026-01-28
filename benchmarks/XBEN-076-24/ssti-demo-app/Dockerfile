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

# Create storage and template directories
RUN mkdir -p /app/storage /app/templates

# Set up flag from build argument - stored in /tmp/flag
# Flag is only accessible via SSTI exploitation
ARG FLAG
RUN echo "${FLAG}" > /tmp/flag && chmod 644 /tmp/flag

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
