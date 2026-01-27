#!/bin/bash
set -e

# Create necessary directories
mkdir -p /var/www/mockapi_server/app/static
mkdir -p /var/www/mockapi_server/app/data

# Inject flag from environment variable into a secrets file
# This file is outside the data directory - should not be directly accessible
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/www/mockapi_server/secrets.txt

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
