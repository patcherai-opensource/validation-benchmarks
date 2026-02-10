#!/bin/bash

# If FLAG env var is set and different from the build-time value, update the flag file
if [ -n "$FLAG" ] && [ "$FLAG" != "PLACEHOLDER_FLAG" ]; then
    echo -n "$FLAG" > /flag
    chmod 644 /flag
fi

# Start Apache in foreground
exec /usr/sbin/apache2ctl -D FOREGROUND
