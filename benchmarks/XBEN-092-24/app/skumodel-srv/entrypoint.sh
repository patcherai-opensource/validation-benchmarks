#!/bin/sh

# Flag is already written to /flag.txt at build time

# Start PHP-FPM
php-fpm -D

# Start Nginx
nginx -g 'daemon off;'
