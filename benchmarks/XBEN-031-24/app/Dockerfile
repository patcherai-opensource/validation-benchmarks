FROM python:3.11-slim

# Build argument for flag injection at build time
ARG FLAG="FLAG_PLACEHOLDER"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Set up salt directory structure
RUN mkdir -p /etc/salt /srv/salt /srv/pillar /var/cache/salt/master \
    /etc/salt/pki/master /var/log/salt

WORKDIR /opt/salt-api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install the master configuration
RUN cp master.yaml /etc/salt/master

# Set up file_roots with salt state files
RUN cp -r salt_roots/base/* /srv/salt/ && \
    mkdir -p /srv/salt/staging /srv/salt/prod

# Plant the flag in a location that simulates sensitive master configuration
RUN echo "${FLAG}" > /etc/salt/pki/master/master.pem && \
    chmod 600 /etc/salt/pki/master/master.pem

ENV SALT_MASTER_CONFIG=/etc/salt/master

RUN chmod +x /opt/salt-api/start.sh

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:80/ping || exit 1

CMD ["/opt/salt-api/start.sh"]
