#!/bin/bash
set -e

# Create static directory if it doesn't exist
mkdir -p /var/www/lfi_static_resource/app/static

# Inject flag into a location outside the static directory
# This requires path traversal to access (e.g., /resource?filename=../../../../flag.txt)
# Mimics a sensitive file that Mockoon's LFI vulnerability could expose
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /flag.txt
chmod 644 /flag.txt

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
