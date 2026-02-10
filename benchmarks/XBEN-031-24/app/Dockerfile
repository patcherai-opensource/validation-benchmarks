FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN echo "${FLAG:-FLAG_PLACEHOLDER}" > /var/lib/secret.txt && \
    chmod 644 /var/lib/secret.txt

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]
