#!/bin/bash

# Set default flag if not provided
if [ -z "$FLAG" ]; then
    FLAG="flag{default-flag-placeholder}"
fi

# Replace the flag placeholder in secret.txt
sed -i "s/@FLAG@/$FLAG/g" secret.txt

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
