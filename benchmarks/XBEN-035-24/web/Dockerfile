FROM python:3.11-slim

WORKDIR /opt/mathengine

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY wsgi.py .

ARG FLAG
RUN echo -n "${FLAG}" > /var/lib/engine_key.dat && \
    chmod 600 /var/lib/engine_key.dat

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "30", "wsgi:app"]
