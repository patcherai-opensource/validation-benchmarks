FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Plant flag at build time into a protected location
ARG FLAG
RUN mkdir -p /opt/froxlor/secret && \
    echo -n "${FLAG}" > /opt/froxlor/secret/config_key.txt && \
    chmod 644 /opt/froxlor/secret/config_key.txt

# Clean up any stale files
RUN rm -f flag.txt instance/urls.db

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

CMD ["python", "app.py"]
