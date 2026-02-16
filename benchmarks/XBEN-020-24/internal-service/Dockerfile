FROM python:3.11-slim

WORKDIR /opt/internal

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.0 gunicorn==21.2.0

COPY internal_app.py .

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:80", "-w", "2", "--access-logfile", "-", "internal_app:app"]
