FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG FLAG="FLAG{placeholder}"
RUN mkdir -p /data && echo "${FLAG}" > /data/system_config.dat && chmod 600 /data/system_config.dat

WORKDIR /app
EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
