#!/bin/bash

# If FLAG environment variable is set, update the flag file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
    chmod 644 /flag
    unset FLAG
fi

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
