#!/bin/bash
set -e

# Write flag from environment variable to file at startup
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /tmp/flag.txt
    chmod 644 /tmp/flag.txt
fi

# Start the application
exec gunicorn --bind 0.0.0.0:80 --workers 1 --timeout 30 app:app
