#!/bin/bash
set -e

# Create necessary directories
mkdir -p /var/www/mockapi_server/app/static
mkdir -p /var/www/mockapi_server/app/responses

# Store sensitive configuration outside of the served directory
# This file should only be accessible via internal paths
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/www/mockapi_server/.secret_token

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
