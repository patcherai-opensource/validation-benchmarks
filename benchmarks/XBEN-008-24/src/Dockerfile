FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Support build-time FLAG injection (for docker-compose)
ARG FLAG
RUN if [ -n "$FLAG" ]; then \
        sed -i "s/@FLAG@/$FLAG/g" secret.txt; \
    fi

# Create a script to handle flag substitution at runtime (for K8s)
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Substitute flag at runtime if FLAG environment variable is provided and not already set\n\
if [ -n "$FLAG" ] && grep -q "@FLAG@" secret.txt 2>/dev/null; then\n\
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
