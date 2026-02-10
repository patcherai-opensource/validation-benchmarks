#!/bin/bash

# If FLAG environment variable is set, update the flag file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
    # Clear the FLAG from environment to prevent access via /proc/self/environ
    unset FLAG
fi

# Also clear FLAG_ENV if set
if [ -n "$FLAG_ENV" ]; then
    unset FLAG_ENV
fi

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
