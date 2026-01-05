#!/bin/bash

# Replace the flag placeholder with the actual flag from environment variable
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" secret.txt
else
    echo "WARNING: FLAG environment variable not set"
    sed -i "s/@FLAG@/FLAG{default_flag}/g" secret.txt
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
