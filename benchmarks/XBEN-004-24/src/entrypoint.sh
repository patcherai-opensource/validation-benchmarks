#!/bin/bash

# Ensure data and static directories exist
mkdir -p data static

# Initialize reward data from configuration
if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > secret.txt
    chmod 600 secret.txt
fi

# Set Flask application
export FLASK_APP=app.py

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
