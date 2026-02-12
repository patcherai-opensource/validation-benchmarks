#!/bin/bash
set -e

# Handle runtime flag substitution if FLAG environment variable is set
# and the file still has the placeholder from the build
if [ -n "$FLAG" ] && [ -f "secret.txt" ]; then
    if grep -q "@FLAG@" secret.txt; then
        sed -i "s/@FLAG@/$FLAG/g" secret.txt
    fi
fi

# Execute the main command
exec "$@"
