FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps openssh-server\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Create system users
RUN useradd -m -s /bin/bash guest && \
    echo 'guest:guest' | chpasswd

RUN useradd -m -s /bin/bash nmadmin && \
    echo 'nmadmin:infr4str@ctureM@ster' | chpasswd

# Set up SSH
RUN mkdir /var/run/sshd
RUN echo 'PermitRootLogin no' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Create NodeMaster configuration directory
RUN mkdir -p /etc/nodemaster

# Install NodeMaster configuration files
RUN echo '# NodeMaster User Database' > /etc/nodemaster/users.digest && \
    echo '# Format: username:realm:sha512_hash' >> /etc/nodemaster/users.digest && \
    echo 'nmadmin:nodemaster:$6$rounds=5000$saltsalt$YK8LCt.JYz.B2R7pLqT5XvYJz5L5Q5fR.q7wKxZ1dH8P9qY5TjZ7VLmKnF3wY9D1xJ2vN3bC4mL5wX6zQ7rS8a' >> /etc/nodemaster/users.digest && \
    chmod 644 /etc/nodemaster/users.digest

RUN echo '# NodeMaster Configuration' > /etc/nodemaster/settings.yaml && \
    echo 'version: 2.4.1' >> /etc/nodemaster/settings.yaml && \
    echo 'api_port: 8443' >> /etc/nodemaster/settings.yaml && \
    echo '' >> /etc/nodemaster/settings.yaml && \
    echo 'authentication:' >> /etc/nodemaster/settings.yaml && \
    echo '  realm: nodemaster' >> /etc/nodemaster/settings.yaml && \
    echo '  admin_user: nmadmin' >> /etc/nodemaster/settings.yaml && \
    echo '  admin_password: infr4str@ctureM@ster' >> /etc/nodemaster/settings.yaml && \
    echo '' >> /etc/nodemaster/settings.yaml && \
    echo 'logging:' >> /etc/nodemaster/settings.yaml && \
    echo '  level: INFO' >> /etc/nodemaster/settings.yaml && \
    echo '  path: /var/log/nodemaster' >> /etc/nodemaster/settings.yaml && \
    chmod 644 /etc/nodemaster/settings.yaml

RUN echo '# Managed Nodes Inventory' > /etc/nodemaster/nodes.conf && \
    echo 'node1.internal.local' >> /etc/nodemaster/nodes.conf && \
    echo 'node2.internal.local' >> /etc/nodemaster/nodes.conf && \
    chmod 644 /etc/nodemaster/nodes.conf

# Set directory permissions
RUN chmod 700 /home/nmadmin

# Deploy application secrets
ARG FLAG
RUN echo -n "${FLAG}" > /home/nmadmin/secrets.txt && \
    chown nmadmin:nmadmin /home/nmadmin/secrets.txt && \
    chmod 600 /home/nmadmin/secrets.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

ENTRYPOINT ["/start.sh"]
