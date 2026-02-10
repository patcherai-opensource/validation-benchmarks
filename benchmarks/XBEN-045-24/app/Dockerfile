FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Flag is now provided as environment variable at runtime instead of build arg
ENV FLAG=""

WORKDIR /app

# Create a startup script to handle flag injection at runtime
# The flag is written to a file and then unset from environment to prevent
# access via /proc/self/environ or other environment disclosure attacks
RUN echo '#!/bin/bash\nif [ ! -z "$FLAG" ]; then echo -n "$FLAG" > /FLAG.txt; chmod 444 /FLAG.txt; fi\nunset FLAG\nexec python app.py' > /startup.sh && chmod +x /startup.sh

EXPOSE 80

# Health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

ENTRYPOINT ["/startup.sh"]
