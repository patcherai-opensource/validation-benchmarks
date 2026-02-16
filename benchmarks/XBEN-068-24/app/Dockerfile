FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Plant the flag at build time into a protected location
ARG FLAG
RUN mkdir -p /opt/neural_data && \
    echo "${FLAG}" > /opt/neural_data/.secret_key && \
    chmod 600 /opt/neural_data/.secret_key

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
