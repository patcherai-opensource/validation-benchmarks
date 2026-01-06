#!/bin/bash

# Inject flag from environment variable at runtime
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /FLAG.txt
else
    echo "Warning: FLAG environment variable not set"
fi

# Start the Flask application
exec python app.py