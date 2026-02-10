#!/bin/bash
set -e

# Write the flag to a file that can only be accessed via the SSTI vulnerability
# The flag is stored in a location that's not directly accessible from the web
if [ -n "$FLAG" ]; then
    echo "$FLAG" > /flag.txt
    chmod 644 /flag.txt
fi

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 80
