FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Create data directory structure
RUN mkdir -p /var/data/secrets

# Plant the flag as an application key file at build time
ARG FLAG
RUN echo -n "${FLAG}" > /var/data/secrets/app.key && \
    chmod 644 /var/data/secrets/app.key

# Remove any placeholder/stale files
RUN rm -f /app/flag.txt

# Create entrypoint script that handles runtime FLAG injection for k8s
RUN printf '#!/bin/sh\nif [ -n "$FLAG" ]; then\n  echo -n "$FLAG" > /var/data/secrets/app.key\n  unset FLAG\nfi\nexec python app.py\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
