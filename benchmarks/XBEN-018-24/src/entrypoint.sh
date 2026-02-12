#!/bin/bash
set -e

# Handle runtime flag substitution for K8s deployment
if [ -n "$FLAG" ] && [ -f "/app/.flag_secret" ]; then
    if grep -q "@FLAG@" /app/.flag_secret; then
        sed -i "s|@FLAG@|$FLAG|g" /app/.flag_secret
    fi
fi

# Ensure static directory exists for temporary render files
mkdir -p /app/static

exec "$@"
