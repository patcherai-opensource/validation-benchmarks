#!/bin/bash
# Update flag file from environment variable if set
if [ ! -z "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi
exec "$@"