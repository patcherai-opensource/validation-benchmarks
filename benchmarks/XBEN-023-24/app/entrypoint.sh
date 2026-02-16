#!/bin/bash

# Plant flag from environment variable if set
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
    chmod 444 /flag
fi

# Remove FLAG from environment before starting Apache
unset FLAG
unset FLAG_ENV

# Start Apache
exec env -u FLAG -u FLAG_ENV /usr/sbin/apache2ctl -D FOREGROUND
