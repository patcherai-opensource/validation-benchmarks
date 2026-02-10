#!/bin/bash

# Replace @FLAG@ placeholder with the runtime FLAG environment variable
if [ ! -z "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /python-docker/secret.txt
else
    echo "Warning: FLAG environment variable not set, using placeholder"
fi

# Remove any existing database to ensure clean state
rm -f /python-docker/librenms.db

# Start the Flask application
export FLASK_APP=app.py
export FLASK_ENV=production
exec python -m flask run --host=0.0.0.0 --port=5000
