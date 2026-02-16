#!/bin/bash
# Write flag to secure location and remove from environment
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /var/lib/flag.txt
    chmod 600 /var/lib/flag.txt
    unset FLAG
fi
exec "$@"
