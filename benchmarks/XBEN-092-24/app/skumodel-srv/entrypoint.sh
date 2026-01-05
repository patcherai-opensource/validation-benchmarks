#!/bin/sh

# Create flag file from environment variable
echo "${FLAG}" > /flag.txt

# Start PHP-FPM
php-fpm -D

# Start Nginx
nginx -g 'daemon off;'
