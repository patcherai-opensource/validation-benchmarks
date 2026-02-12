FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.0 gunicorn==21.2.0

COPY internal_app.py .
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

EXPOSE 8888

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "--workers", "1", "--timeout", "30", "internal_app:app"]
