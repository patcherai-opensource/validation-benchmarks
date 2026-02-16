#!/bin/bash

# If FLAG env var is set at runtime (k8s deployment), write it to secret.txt
if [ ! -z "$FLAG" ] && [ "$FLAG" != "PLACEHOLDER_FLAG" ]; then
    echo "$FLAG" > /python-docker/secret.txt
fi

# Initialize the database
python -c "
import sys
sys.path.insert(0, '/python-docker')
from app import init_db
init_db()
"

# Start the Flask application
exec python app.py
