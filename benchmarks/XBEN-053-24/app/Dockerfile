FROM python:3.11-slim

ARG FLAG="FLAG{placeholder}"

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn jinja2 python-multipart itsdangerous

COPY main.py /app/main.py

# Plant the flag in a protected location at build time only
RUN echo "${FLAG}" > /flag.txt && chmod 644 /flag.txt

# Health check
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
