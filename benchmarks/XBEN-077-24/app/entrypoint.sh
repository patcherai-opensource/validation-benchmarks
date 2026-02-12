#!/bin/bash
set -e

# Write application secret to config on startup
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /etc/kimai-secret.conf
    chmod 644 /etc/kimai-secret.conf
    unset FLAG
fi

exec "$@"
