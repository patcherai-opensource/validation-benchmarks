FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY main.py /app/main.py
COPY templates /app/templates
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["/app/entrypoint.sh"]
