#!/bin/bash

# If FLAG environment variable is set at runtime, update the secret file
if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > /python-docker/secret.txt
fi

# Start the Flask application with threading enabled for concurrent requests
exec python app.py
