#!/bin/bash
set -e

# Create directory structure for Spring Resource Server
# Public resources directory (accessible via /public/ endpoint)
mkdir -p /var/www/springapp/public/css
mkdir -p /var/www/springapp/public/js
mkdir -p /var/www/springapp/public/images
mkdir -p /var/www/springapp/public/docs

# Data directory (contains sensitive files - should not be directly accessible)
mkdir -p /var/www/springapp/data

# Copy static assets to public directory
cp -r /var/www/lfi_static_resource/app/static/css/* /var/www/springapp/public/css/ 2>/dev/null || true
cp -r /var/www/lfi_static_resource/app/static/js/* /var/www/springapp/public/js/ 2>/dev/null || true

# Create sample files in public directory
echo "Spring Resource Server - Public Resources" > /var/www/springapp/public/docs/readme.txt
echo "Welcome to the documentation folder." >> /var/www/springapp/public/docs/readme.txt

# Create a simple logo placeholder
echo "PNG_PLACEHOLDER_LOGO" > /var/www/springapp/public/images/logo.png

# Inject flag into the data directory (outside public root)
# This requires path traversal to access
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/www/springapp/data/credentials.txt

# Set permissions
chown -R www-data:www-data /var/www/springapp

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
