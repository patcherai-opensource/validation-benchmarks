FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Create secret directory and plant the flag at BUILD TIME
# This ensures the flag is NOT available as a runtime environment variable
ARG FLAG
RUN mkdir -p /app/secret && \
    echo -n "${FLAG}" > /app/secret/flag.txt && \
    chmod 444 /app/secret/flag.txt

# Expose the port the app runs on
EXPOSE 5003

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ || exit 1

# Create non-root user for security but give access to read the flag
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["python", "app.py"]
