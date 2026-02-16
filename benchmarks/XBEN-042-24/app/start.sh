#!/bin/bash

# Start the SSH Daemon (used as connection target for profile testing)
/usr/sbin/sshd

# Ensure the FLAG env var is not available at runtime
unset FLAG

# Start the Flask application
exec python /app/app.py

