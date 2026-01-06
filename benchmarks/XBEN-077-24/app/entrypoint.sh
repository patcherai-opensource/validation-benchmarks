#!/bin/bash
set -e

# Substitute FLAG placeholder with the environment variable value
if [ -n "$FLAG" ]; then
    sed -i "s/FLAG/$FLAG/g" /app/flag.txt
fi

# Execute the CMD
exec "$@"
