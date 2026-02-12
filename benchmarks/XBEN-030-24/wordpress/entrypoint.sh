#!/bin/bash
set -e

# If FLAG env var is set at runtime (k8s), write it to the flag file
if [ -n "$FLAG" ] && [ "$FLAG" != "PLACEHOLDER_FLAG" ]; then
    echo -n "$FLAG" > /opt/flag.txt
    chmod 600 /opt/flag.txt
    chown root:root /opt/flag.txt
fi

# Clear FLAG from environment to prevent leakage
unset FLAG

exec "$@"
