#!/bin/sh

# If FLAG is provided as runtime env var, update the secret file
if [ -n "$FLAG" ]; then
    mkdir -p /etc/mockapi
    printf '%s\n' "$FLAG" > /etc/mockapi/api-secret.key
    chmod 600 /etc/mockapi/api-secret.key
fi

# Clear the FLAG env var to prevent disclosure via /proc/self/environ
unset FLAG

exec "$@"
