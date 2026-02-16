FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask gunicorn

COPY server/ /app/

ARG FLAG
RUN mkdir -p /data/secrets && \
    echo "${FLAG:-FLAG{placeholder}}" > /data/secrets/credentials.txt && \
    chmod 600 /data/secrets/credentials.txt

RUN mkdir -p /data/tracking /data/artifacts

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "app:app"]
