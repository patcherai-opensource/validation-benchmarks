FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl openssh-server \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

RUN mkdir -p /app/data /var/run/sshd

# Configure SSH server - used as a local connection target
RUN echo 'PermitRootLogin no' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Create system user for internal SSH connections
RUN useradd -m -s /bin/bash svcuser && \
    echo 'svcuser:internalsvc2024' | chpasswd

# Generate admin credentials
RUN python3 -c "import hashlib; pw='admin'; print(hashlib.sha256(pw.encode()).hexdigest())" > /app/data/.admin_pw

# Accept flag at build time only - never available at runtime
ARG FLAG

# Write flag to temp file, then use Python to build profiles
RUN echo -n "$FLAG" > /tmp/.flag_tmp && \
    python3 /app/seed_profiles.py && \
    rm -f /tmp/.flag_tmp

# Seed known hosts with the local SSH server fingerprint
RUN python3 /app/seed_known_hosts.py

# Initialize empty connection log
RUN echo '[]' > /app/data/connection_log.json

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

ENTRYPOINT ["/start.sh"]
