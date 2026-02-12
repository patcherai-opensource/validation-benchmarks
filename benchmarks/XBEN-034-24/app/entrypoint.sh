#!/bin/bash

# Write flag to file if provided via environment
if [ -n "${FLAG:-}" ] && [ "${FLAG}" != "FLAG_PLACEHOLDER" ]; then
    echo -n "$FLAG" > /flag.txt
    chmod 444 /flag.txt
fi

# Start supervisord
exec /usr/bin/supervisord
