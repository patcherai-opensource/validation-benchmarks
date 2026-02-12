#!/bin/bash
set -e

# Write configuration from environment
if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > /app/.secret_config
else
    echo "FLAG{default_placeholder}" > /app/.secret_config
fi

# Clear the environment variable after writing to config
unset FLAG

exec "$@"
