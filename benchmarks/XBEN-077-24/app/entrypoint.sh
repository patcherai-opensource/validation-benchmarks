#!/bin/bash
set -e

# Substitute FLAG placeholder with the environment variable value
if [ -n "$FLAG" ]; then
    sed -i "s/FLAG/$FLAG/g" /app/flag.txt
    # Clear the FLAG environment variable to prevent alternative access paths
    unset FLAG
fi

# Execute the CMD
exec "$@"
