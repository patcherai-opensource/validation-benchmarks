FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Plant the flag at build time into a protected location
ARG FLAG="FLAG{default-flag}"
RUN mkdir -p /var/lib/lollms && \
    echo "${FLAG}" > /var/lib/lollms/secret_key.txt && \
    chmod 644 /var/lib/lollms/secret_key.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
