#!/bin/bash
set -e

# Replace the flag placeholder with the environment variable
if [ ! -z "$FLAG" ]; then
    # Use a different delimiter to avoid issues with special characters in FLAG
    sed -i "s|<FLAG>|$FLAG|g" /var/www/html/index.php
else
    sed -i "s|<FLAG>|FLAG{default_placeholder}|g" /var/www/html/index.php
fi

# Execute the original command
exec "$@"
