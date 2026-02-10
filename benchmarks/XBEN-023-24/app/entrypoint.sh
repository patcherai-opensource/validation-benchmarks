#!/bin/bash

# If FLAG environment variable is set, update the flag file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
