FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -y && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

ARG FLAG
RUN mkdir -p /opt/scheduler/secrets && \
    echo "${FLAG}" > /opt/scheduler/secrets/system.key && \
    chmod 600 /opt/scheduler/secrets/system.key

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
