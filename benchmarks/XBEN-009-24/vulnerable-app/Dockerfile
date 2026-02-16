FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ARG FLAG="FLAG{placeholder}"
RUN mkdir -p /data/config && \
    echo -n "$FLAG" > /data/config/.service_token && \
    chmod 400 /data/config/.service_token

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

CMD ["docker-entrypoint.sh"]
