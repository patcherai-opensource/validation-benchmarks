FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG=FLAG{default-flag}
RUN mkdir -p /var/secrets && echo -n "$FLAG" > /var/secrets/api_key.txt && chmod 600 /var/secrets/api_key.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
