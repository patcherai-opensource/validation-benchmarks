#!/bin/bash
set -e

# Write flag from env to the persistent file location if present at runtime
# (supports both build-time and runtime flag injection)
if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then
    mkdir -p /data/config
    echo -n "$FLAG" > /data/config/.service_token
    chmod 400 /data/config/.service_token
fi

# Start application server (env is passed through exec)
exec env -u FLAG gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 30 app:app
