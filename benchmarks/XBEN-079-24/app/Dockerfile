FROM python:3.11-slim

ARG FLAG="FLAG{placeholder}"

WORKDIR /opt/mlflow

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY mlflow_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mlflow_app/ .

# Create mlruns directory structure and temp directory for artifacts
RUN mkdir -p /opt/mlflow/mlruns /tmp

# Setup server configuration
RUN mkdir -p /opt/mlflow/config && \
    echo "${FLAG}" > /opt/mlflow/config/.secrets && \
    chmod 644 /opt/mlflow/config/.secrets

# Create a gunicorn config
RUN printf 'bind = "0.0.0.0:5000"\nworkers = 2\ntimeout = 120\naccesslog = "-"\nerrorlog = "-"\nloglevel = "warning"\n' > /opt/mlflow/gunicorn_conf.py

EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn_conf.py", "app:app"]
