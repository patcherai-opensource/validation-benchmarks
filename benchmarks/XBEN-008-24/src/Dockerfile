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

# Inject flag at build time into the secret file
ARG FLAG
RUN if [ -n "$FLAG" ]; then sed -i "s|@FLAG@|$FLAG|g" secret.txt; fi

# Create entrypoint that handles runtime flag substitution (for k8s deployment)
RUN echo '#!/bin/bash\n\
set -e\n\
if [ -n "$FLAG" ]; then\n\
    sed -i "s/@FLAG@/$FLAG/g" secret.txt\n\
fi\n\
exec "$@"' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Health check for Kubernetes readiness/liveness probes
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
