#!/bin/bash
set -e

# Write the flag to a secure location (only accessible via RCE)
if [ -n "$FLAG" ]; then
    echo "$FLAG" > /flag.txt
    chmod 644 /flag.txt
fi

# Remove the placeholder flag file from app directory
rm -f /app/flag.txt

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 80
