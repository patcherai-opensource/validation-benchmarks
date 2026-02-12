#!/bin/bash
set -e

# Handle flag substitution at runtime
if [ -n "$FLAG" ]; then
    find /docker-entrypoint-initdb.d/ -name "*.sql" -exec sed -i "s|@FLAG@|$FLAG|g" {} + 2>/dev/null || true
fi
mv /docker-entrypoint-initdb.d/init-template.sql /docker-entrypoint-initdb.d/init.sql 2>/dev/null || true

# Call the original MySQL entrypoint
exec /usr/local/bin/original-entrypoint.sh "$@"
