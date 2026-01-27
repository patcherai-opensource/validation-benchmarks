FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Flag can be provided as build arg or environment variable at runtime
ARG FLAG=""
ENV FLAG=${FLAG}

WORKDIR /app

# Startup script
RUN echo '#!/bin/bash\nexec python app.py' > /startup.sh && chmod +x /startup.sh

EXPOSE 80

# Health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

ENTRYPOINT ["/startup.sh"]
