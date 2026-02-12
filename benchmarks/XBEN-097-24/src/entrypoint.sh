#!/bin/bash
set -e

# Create log directory
mkdir -p /var/log/uwsgi

# Runtime flag substitution - if FLAG env var is set and differs from current file content
if [ ! -z "${FLAG:-}" ]; then
    echo "$FLAG" > /var/www/flag.txt
    chmod 644 /var/www/flag.txt
fi

# Clear the FLAG from environment to prevent leaking via /proc/self/environ
unset FLAG

# Start the uWSGI PHP server
exec python3 /opt/server.py
