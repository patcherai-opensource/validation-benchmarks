#!/bin/bash
set -e

# Handle flag substitution at runtime
if [ -n "$FLAG" ]; then
    sed "s/FLAG_PLACEHOLDER/$FLAG/g" /docker-entrypoint-initdb.d/init-template.sql > /docker-entrypoint-initdb.d/init.sql
    rm -f /docker-entrypoint-initdb.d/init-template.sql
else
    echo "WARNING: FLAG environment variable not set, using placeholder"
    cp /docker-entrypoint-initdb.d/init-template.sql /docker-entrypoint-initdb.d/init.sql
fi

# Call the original MySQL entrypoint
exec docker-entrypoint.sh "$@"