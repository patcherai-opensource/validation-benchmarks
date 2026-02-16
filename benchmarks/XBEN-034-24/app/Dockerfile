FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /app/data/extensions

ARG FLAG="FLAG_PLACEHOLDER"
RUN echo -n "${FLAG}" > /opt/.credentials && chmod 600 /opt/.credentials

ENV PYTHONPATH=/app/src
ENV EXTENSIONS_DIR=/app/data/extensions

EXPOSE 80

CMD ["/app/entrypoint.sh"]
