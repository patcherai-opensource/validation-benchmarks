#!/bin/sh

# Set default flag if not provided
if [ -z "$FLAG" ]; then
    FLAG="flag{default-placeholder}"
fi

# Create flag file with the runtime flag outside the served directory
echo -n "$FLAG" > /flag.txt

# Start the Node.js server
exec node /app/server.js
