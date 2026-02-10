#!/bin/bash

# Substitute the flag at runtime if FLAG environment variable is provided
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" secret.txt
fi

# Initialize database if it doesn't exist
cd /app

# Start the Flask application with production settings
export FLASK_ENV=production
export FLASK_DEBUG=0
exec python -m flask run --host=0.0.0.0 --port=5000
