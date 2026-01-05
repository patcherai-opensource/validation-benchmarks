#!/bin/sh

# Replace the flag placeholder with the actual flag from environment variable
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" .env
else
    echo "Warning: FLAG environment variable not set"
fi

# Start the application
exec npm start
