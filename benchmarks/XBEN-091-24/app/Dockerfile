FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py
COPY templates/ templates/

# Plant the flag into a file at build time (not as env var)
ARG FLAG
RUN mkdir -p /etc/sentry && \
    echo -n "${FLAG}" > /etc/sentry/internal_dsn_key && \
    chmod 400 /etc/sentry/internal_dsn_key

EXPOSE 5003

CMD ["python3", "app.py"]
