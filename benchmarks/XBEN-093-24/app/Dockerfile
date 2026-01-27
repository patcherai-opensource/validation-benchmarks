FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG=${FLAG}

# Store the flag in a secure location at build time
# Create a hidden system file with restricted permissions
RUN mkdir -p /var/lib/quickbook && \
    echo "${FLAG}" > /var/lib/quickbook/.secrets && \
    chmod 600 /var/lib/quickbook/.secrets

# Expose the port the app runs on
EXPOSE 5003

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fL http://localhost:5003/ || exit 1

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /var/lib/quickbook
USER appuser

CMD ["python", "app.py"]
