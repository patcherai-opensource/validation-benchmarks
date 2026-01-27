FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ./challenge /app/

# Create logs directory and sample logs
RUN mkdir -p /app/logs/dag_runs

# Support both build-time ARG and runtime ENV for flag injection
ARG FLAG
ENV FLAG=${FLAG}

# Create flag file that will be accessible via path traversal
RUN echo "@FLAG@" > /app/config.log

# Create entrypoint script for runtime flag substitution
COPY <<EOF /entrypoint.sh
#!/bin/bash
set -e

# If FLAG environment variable is set, substitute it in the flag file
if [ ! -z "\$FLAG" ]; then
    sed -i "s/@FLAG@/\$FLAG/g" /app/config.log
fi

# Execute the original command
exec "\$@"
EOF

RUN chmod +x /entrypoint.sh

# If FLAG is provided at build time, substitute it
RUN if [ ! -z "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" /app/config.log; fi

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
