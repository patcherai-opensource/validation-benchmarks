FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps openssh-server\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Create service account for configuration management
RUN useradd -m -s /bin/bash configadmin && \
    echo 'configadmin:sysadmin2024' | chpasswd

# Create configuration directory with sensitive files
# NOTE: Files deployed with default 0644 permissions (world-readable)
# This is a security misconfiguration - sensitive files should be 0640
RUN mkdir -p /etc/nodeconfig

# Create users.digest file with hashed credentials
# Format: username:realm:sha512_hash
RUN echo "# NodeConfig User Digest File" > /etc/nodeconfig/users.digest && \
    echo "# Format: username:realm:password_sha512_hash" >> /etc/nodeconfig/users.digest && \
    echo "# WARNING: Ensure proper file permissions are set" >> /etc/nodeconfig/users.digest && \
    echo "" >> /etc/nodeconfig/users.digest && \
    echo "configadmin:nodeconfig:457563bed4b6da0d2208c33638d7b9c553101a63c55b4d19592ad81d821a5b9f4957232b206ec0ddce058c4000c6db5801728c2bf5427f70cb7837268bf1c897" >> /etc/nodeconfig/users.digest

# Create settings.yaml configuration file
RUN echo "# NodeConfig Settings" > /etc/nodeconfig/settings.yaml && \
    echo "system:" >> /etc/nodeconfig/settings.yaml && \
    echo "  name: NodeConfig Manager" >> /etc/nodeconfig/settings.yaml && \
    echo "  version: 2.1.4" >> /etc/nodeconfig/settings.yaml && \
    echo "  config_dir: /etc/nodeconfig" >> /etc/nodeconfig/settings.yaml && \
    echo "" >> /etc/nodeconfig/settings.yaml && \
    echo "security:" >> /etc/nodeconfig/settings.yaml && \
    echo "  hash_algorithm: sha512" >> /etc/nodeconfig/settings.yaml && \
    echo "  auth_realm: nodeconfig" >> /etc/nodeconfig/settings.yaml && \
    echo "" >> /etc/nodeconfig/settings.yaml && \
    echo "backup:" >> /etc/nodeconfig/settings.yaml && \
    echo "  enabled: true" >> /etc/nodeconfig/settings.yaml && \
    echo "  endpoint: /backup/" >> /etc/nodeconfig/settings.yaml

# Set world-readable permissions (security misconfiguration)
RUN chmod 644 /etc/nodeconfig/users.digest && \
    chmod 644 /etc/nodeconfig/settings.yaml

RUN mkdir /var/run/sshd
RUN echo 'PermitRootLogin no' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Support both build-time ARG and runtime ENV for FLAG
ARG FLAG
ENV FLAG=${FLAG}

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

ENTRYPOINT ["/start.sh"]
