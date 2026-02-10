#!/bin/bash
set -e

# Create required directories
mkdir -p /var/www/lfi_static_resource/app/static
mkdir -p /var/data

# Store sensitive data in a separate directory
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/data/.secret

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
