#!/bin/bash
set -e

# Handle runtime flag substitution if FLAG environment variable is set
if [ -n "$FLAG" ] && [ -f "secret.txt" ]; then
    # Check if the file still has the placeholder
    if grep -q "@FLAG@" secret.txt; then
        echo "Substituting FLAG placeholder with environment variable..."
        sed -i "s/@FLAG@/$FLAG/g" secret.txt
    fi
fi

# Execute the main command
exec "$@"