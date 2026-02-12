#!/bin/bash

# Initialize application configuration
if [ ! -z "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /python-docker/secret.txt
    unset FLAG
else
    echo "Warning: FLAG environment variable not set, using placeholder"
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
