FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Flag is provided as environment variable at runtime
ENV FLAG=""

WORKDIR /app

# Create startup script that places flag and starts the app
RUN printf '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /var/lib/mediaflow/.secret_key\n  chmod 600 /var/lib/mediaflow/.secret_key\nfi\nunset FLAG\nexec python app.py\n' > /startup.sh && chmod +x /startup.sh

RUN mkdir -p /var/lib/mediaflow

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/health || exit 1

ENTRYPOINT ["/startup.sh"]
