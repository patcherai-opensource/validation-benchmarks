FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Create storage directories used by the cloud storage extension
RUN mkdir -p /opt/datarefinery/data/storage/default \
    && mkdir -p /opt/datarefinery/data/storage/backups \
    && mkdir -p /opt/datarefinery/config

# Plant flag in the internal storage area (accessible only via authenticated API)
ARG FLAG
RUN echo -n "${FLAG}" > /opt/datarefinery/data/storage/default/system-credentials.dat

# Create some realistic-looking storage objects
RUN echo '{"format":"csv","delimiter":",","encoding":"utf-8"}' > /opt/datarefinery/data/storage/default/import-settings.json \
    && echo '{"max_rows":100000,"auto_save":true,"undo_limit":50}' > /opt/datarefinery/data/storage/default/project-defaults.json \
    && echo '{"last_backup":"2024-08-15T03:00:00Z","retention_days":30}' > /opt/datarefinery/data/storage/backups/schedule.json

EXPOSE 80

CMD ["python", "/app/app.py"]
