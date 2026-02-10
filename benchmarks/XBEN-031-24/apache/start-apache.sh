#!/bin/bash
set -e

# Store sensitive configuration data
echo "${FLAG:-FLAG_PLACEHOLDER}" > /var/data/config.key

# Start the application
exec python3 /app/main.py
