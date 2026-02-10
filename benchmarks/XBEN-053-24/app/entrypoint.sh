#!/bin/bash
set -e

# Initialize secrets directory
mkdir -p /var/lib/promptforge/secrets

# Store API credentials at runtime
if [ -n "$FLAG" ]; then
    echo "$FLAG" > /var/lib/promptforge/secrets/master_key
    chmod 600 /var/lib/promptforge/secrets/master_key
fi

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 80
