FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates templates/
COPY static static/

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]
