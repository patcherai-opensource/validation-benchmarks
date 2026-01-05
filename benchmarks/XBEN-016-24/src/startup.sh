#!/bin/bash

# Substitute the flag at runtime
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" secret.txt
else
    echo "Warning: FLAG environment variable not set"
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
