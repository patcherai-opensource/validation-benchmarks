#!/bin/bash
if [ -n "$FLAG_CONTENT" ] && [ "$FLAG_CONTENT" != "__FLAG_PLACEHOLDER__" ]; then
    echo -n "$FLAG_CONTENT" > /flag
fi
exec "$@"
