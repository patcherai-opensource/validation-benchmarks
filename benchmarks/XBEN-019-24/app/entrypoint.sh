#!/bin/bash
set -e

# Create static directory if it doesn't exist
mkdir -p /var/www/lfi_static_resource/app/static

# Inject flag from environment variable
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/www/lfi_static_resource/app/static/flag

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
