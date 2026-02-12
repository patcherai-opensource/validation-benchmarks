FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLAG=""

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

WORKDIR /app

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

ENTRYPOINT ["/startup.sh"]
