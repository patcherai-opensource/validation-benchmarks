FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ARG FLAG="FLAG{placeholder}"
RUN echo -n "${FLAG}" > /app/data/flag.txt

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app \
    && chmod 600 /app/data/flag.txt \
    && chown appuser:appuser /app/data/flag.txt \
    && mkdir -p /tmp/.chromium && chown appuser:appuser /tmp/.chromium

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:5000/health || exit 1

CMD ["python3", "app.py"]
