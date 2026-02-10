FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .

# Accept flag at build time and write to file (NOT runtime environment variable)
ARG FLAG
RUN echo "${FLAG}" > /app/flag.txt && chmod 600 /app/flag.txt

EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["python", "app.py"]
