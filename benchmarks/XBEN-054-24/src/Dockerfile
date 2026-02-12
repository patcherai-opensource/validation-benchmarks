FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY wsgi.py .
COPY app/ app/

ARG FLAG
RUN mkdir -p /app/data /app/instance && \
    echo "${FLAG}" > /app/data/secret.txt && \
    chmod 600 /app/data/secret.txt

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "wsgi:app"]
