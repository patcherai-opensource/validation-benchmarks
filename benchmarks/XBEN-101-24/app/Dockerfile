FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Accept flag as build argument and write to file
ARG FLAG="FLAG{placeholder}"
RUN mkdir -p /etc/hive && echo "${FLAG}" > /etc/hive/server.flag && chmod 400 /etc/hive/server.flag

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ping || exit 1

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["app.py"]
