#!/bin/bash

# Inject flag from environment variable at runtime
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
    chmod 600 /flag.txt
else
    echo "Warning: FLAG environment variable not set"
fi

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:80 --workers 2 --timeout 120 app:app
