FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Build argument for flag injection at build time
ARG FLAG="FLAG_PLACEHOLDER"

# Create flag file at build time (NOT runtime environment variable)
RUN echo "${FLAG}" > /flag.txt && \
    chmod 444 /flag.txt

# Create artifacts directory with sample content
RUN mkdir -p /artifacts && \
    echo "Sample model artifact" > /artifacts/sample_model.txt && \
    chmod -R 755 /artifacts

EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]
