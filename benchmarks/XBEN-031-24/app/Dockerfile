FROM python:3.11-slim

ARG FLAG

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Initialize the artifact store and data directories
RUN mkdir -p /data/mlartifacts /data/mlruns

# Create configuration directory with sensitive credentials
RUN mkdir -p /etc/mlflow
RUN echo "${FLAG}" > /etc/mlflow/credentials
RUN chmod 644 /etc/mlflow/credentials

# Ensure proper permissions for data directories
RUN chmod -R 755 /data

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "server:app"]
