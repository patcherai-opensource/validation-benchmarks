FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Accept the flag as a build argument and write it to a secure location
ARG FLAG=""
RUN echo -n "$FLAG" > /opt/.credentials && chmod 600 /opt/.credentials

# Also support runtime FLAG injection for k8s deployment
ENV FLAG=""

# Startup script: if FLAG env is set at runtime, update the credentials file
RUN printf '#!/bin/bash\nif [ -n "$FLAG" ]; then echo -n "$FLAG" > /opt/.credentials; fi\nunset FLAG\nexec env -u FLAG python app.py\n' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
