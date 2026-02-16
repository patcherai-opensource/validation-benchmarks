FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-mysql-client \
        netcat-openbsd \
        curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN chmod +x /app/entrypoint.sh

ARG FLAG
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/db_init.sql

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
