
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Install required packages
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN chmod +x /app/entrypoint.sh

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["/app/entrypoint.sh"]
