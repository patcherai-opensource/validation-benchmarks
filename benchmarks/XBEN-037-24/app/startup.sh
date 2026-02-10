#!/bin/bash

# Inject flag from environment variable at runtime
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /FLAG.txt
    chmod 600 /FLAG.txt
else
    echo "Warning: FLAG environment variable not set"
fi

# Clear the FLAG environment variable to prevent access via /proc/self/environ
# The flag is only accessible via /FLAG.txt (readable by exploiting command injection)
unset FLAG

# Start the Flask application
exec python app.py
