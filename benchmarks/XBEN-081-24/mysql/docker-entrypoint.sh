#!/bin/bash
set -e

# Handle flag substitution at runtime
if [ -n "$FLAG" ]; then
    find /docker-entrypoint-initdb.d/ -name "*.sql" -exec sed -i "s|@FLAG@|$FLAG|g" {} + || true
fi

# Call the original MySQL entrypoint
exec docker-entrypoint.sh "$@"
