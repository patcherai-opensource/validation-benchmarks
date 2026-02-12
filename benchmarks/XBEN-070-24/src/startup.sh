#!/bin/bash

# If FLAG is provided as env var and secret.txt is empty or has placeholder, update it
if [ ! -z "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then
    echo "$FLAG" > secret.txt
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
