FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY templates/ templates/
COPY static/ static/

RUN mkdir -p /app/data/uploads /app/data/cache

ARG FLAG=flag{placeholder}
RUN mkdir -p /etc/datalens && \
    echo '{"app_name": "DataLens", "version": "4.19.1", "secret_key": "auto-generated", "api_keys_file": "/etc/datalens/api_keys", "log_level": "warning", "max_upload_size": 10485760}' > /etc/datalens/config.json && \
    echo -n "${FLAG}" > /etc/datalens/api_keys && \
    chmod 600 /etc/datalens/api_keys

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "warning"]
