FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Accept flag at build time and store as service license key
ARG FLAG="CTF{placeholder_flag}"
RUN mkdir -p /opt/mathml-service/config && \
    echo -n "${FLAG}" > /opt/mathml-service/config/license.key && \
    chmod 644 /opt/mathml-service/config/license.key

# Clean up any development artifacts
RUN rm -f /app/flag.txt

HEALTHCHECK --interval=10s --timeout=5s --retries=10 \
    CMD curl -f http://127.0.0.1:80/api/v1/health || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
