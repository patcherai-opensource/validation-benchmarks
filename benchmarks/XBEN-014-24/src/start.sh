#!/bin/bash
set -e

# Replace the flag placeholder with the actual flag from environment variable
if [ ! -z "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /var/www/html/index.php
fi

# Start Apache
exec apache2-foreground