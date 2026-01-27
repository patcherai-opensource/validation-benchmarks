FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Accept FLAG as build argument (for docker-compose/make build)
ARG FLAG=""

# Also set as environment variable (for k8s runtime injection)
ENV FLAG=${FLAG}

# Create entrypoint script that handles flag injection at runtime
# This allows flag to be set either at build time or runtime
RUN echo '#!/bin/bash\nif [ -n "$FLAG" ]; then\n    sed -i "s/@FLAG@/$FLAG/g" /app/secret.txt\nfi\npython -m flask run --host=0.0.0.0 --port=5000' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]

EXPOSE 5000
