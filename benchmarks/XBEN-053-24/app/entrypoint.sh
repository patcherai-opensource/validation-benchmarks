#!/bin/bash
set -e

# Substitute FLAG placeholder with actual flag from environment variable
if [ -n "$FLAG" ]; then
    sed -i "s/FLAG/$FLAG/g" /app/flag.txt
fi

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 80
