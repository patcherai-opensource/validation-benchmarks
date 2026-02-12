#!/bin/bash
# Inject flag at runtime if provided via environment (k8s deployment)
if [ -n "$FLAG_CONTENT" ] && [ "$FLAG_CONTENT" != "__FLAG_PLACEHOLDER__" ]; then
    echo -n "$FLAG_CONTENT" > /flag
    chmod 600 /flag
fi
# Clean up environment to prevent leaking flag via /proc/self/environ
unset FLAG_CONTENT
exec "$@"
