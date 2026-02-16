FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

WORKDIR /app

# Store service API key during build
ARG FLAG
RUN mkdir -p /etc/geodata && \
    echo -n "${FLAG}" > /etc/geodata/api.key && \
    chmod 644 /etc/geodata/api.key

# Remove any placeholder files
RUN rm -f /app/flag.txt

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/health || exit 1

EXPOSE 80

CMD ["python", "app.py"]
