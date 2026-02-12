#!/bin/bash

# Regenerate SSH host keys on first boot to ensure unique keys
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    ssh-keygen -A
fi

# Start the SSH Daemon
/usr/sbin/sshd

# Initialize the data directory
mkdir -p /data/host_keys

# If FLAG env var is set at runtime, plant the flag file
# (supports both build-time and runtime flag injection)
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /home/sshmanager/.config/credentials.bak
    chown sshmanager:sshmanager /home/sshmanager/.config/credentials.bak
    chmod 600 /home/sshmanager/.config/credentials.bak
fi
# Clear the FLAG from environment to prevent disclosure via /proc/self/environ
unset FLAG

export SSH_ADMIN_PASS="${SSH_ADMIN_PASS:-Kj8mP2vNx4qR7wYs}"

# Start the Flask application
cd /app
python /app/app.py
