#!/bin/bash
set -e
exec gunicorn --bind 0.0.0.0:80 --workers 2 --chdir /var/www/webapp app:app
