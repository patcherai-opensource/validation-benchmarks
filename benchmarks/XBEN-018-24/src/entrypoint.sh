#!/bin/bash
set -e

# Handle runtime flag substitution for K8s deployment
if [ -n "$FLAG" ] && [ -f "secret.txt" ]; then
    if grep -q "@FLAG@" secret.txt; then
        sed -i "s/@FLAG@/$FLAG/g" secret.txt
    fi
fi

exec "$@"
