#!/bin/bash

# Replace @FLAG@ placeholder with the runtime FLAG environment variable
if [ ! -z "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /python-docker/secret.txt
fi

# Unset FLAG to prevent leaking via /proc/self/environ
unset FLAG

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
