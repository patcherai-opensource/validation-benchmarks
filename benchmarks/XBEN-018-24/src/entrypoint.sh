#!/bin/bash
set -e

# Handle runtime flag substitution if FLAG environment variable is set
# This supports K8s deployment where FLAG is passed at runtime
if [ -n "$FLAG" ] && [ -f "secret.txt" ]; then
    if grep -q "@FLAG@" secret.txt || grep -q "PLACEHOLDER" secret.txt; then
        echo "$FLAG" > secret.txt
    fi
fi

# Execute the main command
exec "$@"
