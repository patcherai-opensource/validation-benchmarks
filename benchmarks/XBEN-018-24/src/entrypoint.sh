#!/bin/bash
set -e

# Handle runtime flag substitution if FLAG environment variable is set
if [ -n "$FLAG" ] && [ -f "secret.txt" ]; then
    if grep -q "@FLAG@" secret.txt; then
        sed -i "s/@FLAG@/$FLAG/g" secret.txt
    fi
fi

# Execute the main command
exec "$@"