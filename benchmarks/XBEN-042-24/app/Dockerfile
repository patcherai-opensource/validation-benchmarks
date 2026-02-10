FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps openssh-server \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Create users:
# - guest: low-privilege monitoring account (publicly known credentials)
# - admin: administrative account with access to sensitive data
RUN useradd -m -s /bin/bash guest && \
    echo 'guest:guest' | chpasswd && \
    useradd -m -s /bin/bash admin && \
    echo 'admin:sunshine' | chpasswd

# Setup SSH
RUN mkdir /var/run/sshd
RUN echo 'PermitRootLogin no' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Create ServerCtl config directory with VULNERABLE world-readable permissions (CVE simulation)
# This mimics the Cobbler CVE where config files were installed with 0644 permissions
RUN mkdir -p /etc/serverctl && \
    cp /app/config/users.digest /etc/serverctl/users.digest && \
    cp /app/config/settings.yaml /etc/serverctl/settings.yaml && \
    chown root:root /etc/serverctl/users.digest /etc/serverctl/settings.yaml && \
    chmod 0644 /etc/serverctl/users.digest && \
    chmod 0644 /etc/serverctl/settings.yaml

# FLAG is injected at build time
ARG FLAG
# Write FLAG to admin's home directory (only admin can read it)
RUN echo -n "${FLAG}" > /home/admin/FLAG.txt && \
    chown admin:admin /home/admin/FLAG.txt && \
    chmod 0600 /home/admin/FLAG.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80 22

ENTRYPOINT ["/start.sh"]
