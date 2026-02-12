#!/bin/bash
set -e

# Handle runtime flag substitution if FLAG environment variable is set
if [ -n "$FLAG" ] && [ -f "secret.txt" ]; then
    # Check if the file still has the placeholder or needs updating
    if grep -q "@FLAG@" secret.txt; then
        sed -i "s/@FLAG@/$FLAG/g" secret.txt
    fi
fi

# Unset the environment variable after writing to file
unset FLAG

# Execute the main command
exec "$@"
