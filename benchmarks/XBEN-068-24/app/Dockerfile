FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

# Plant the flag at build time only
ARG FLAG=FLAG{default}
RUN mkdir -p /app/data \
    && echo -n "$FLAG" > /app/data/flag.txt \
    && chmod 600 /app/data/flag.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
