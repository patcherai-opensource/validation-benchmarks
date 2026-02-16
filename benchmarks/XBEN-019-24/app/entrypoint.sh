#!/bin/bash
set -e

# Ensure cache directory permissions
chmod -R 755 /var/lib/vizboard/cache

cd /var/www/vizboard
exec gunicorn --bind 0.0.0.0:80 --workers 2 --timeout 120 "app:app"
