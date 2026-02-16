FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn pydantic

WORKDIR /app

COPY main.py /app/main.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /var/secrets /data

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -f http://localhost:80/ping || exit 1

CMD ["/app/entrypoint.sh"]
