FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a script to handle flag substitution at runtime
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Substitute flag at runtime if FLAG environment variable is provided\n\
if [ -n "$FLAG" ]; then\n\
    sed -i "s/@FLAG@/$FLAG/g" secret.txt\n\
fi\n\
\n\
# Execute the main command\n\
exec "$@"' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Health check for Kubernetes readiness/liveness probes
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
