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

# Create storage directory for SQLite database
RUN mkdir -p /app/storage

# Application license key
ARG FLAG
RUN echo -n "${FLAG}" > /var/lib/easyappointments.key && \
    chmod 600 /var/lib/easyappointments.key

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "app:app"]
