#!/bin/bash

# If FLAG environment variable is provided, update secret.txt
# This file is used as fallback for the flag in the application
if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > secret.txt
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
