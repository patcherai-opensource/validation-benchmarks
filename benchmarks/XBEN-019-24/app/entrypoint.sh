#!/bin/bash
set -e

# The flag is already injected at build time into /var/www/lfi_static_resource/secrets/flag.txt
# No runtime flag injection needed

# Ensure directories exist
mkdir -p /var/www/lfi_static_resource/app/public/css
mkdir -p /var/www/lfi_static_resource/app/public/js

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
