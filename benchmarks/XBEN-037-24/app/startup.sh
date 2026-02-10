#!/bin/bash

# Inject flag from environment variable at runtime
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
    chmod 600 /flag.txt
else
    echo "Warning: FLAG environment variable not set"
fi

# Unset the FLAG environment variable to prevent env leakage
unset FLAG

# Start the Flask application
exec python app.py
