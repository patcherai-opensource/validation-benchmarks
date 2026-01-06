#!/bin/bash

# Substitute the flag at runtime if FLAG environment variable is provided
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" secret.txt
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
