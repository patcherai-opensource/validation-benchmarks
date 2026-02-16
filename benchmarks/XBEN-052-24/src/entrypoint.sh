#!/bin/bash
set -e

# Handle runtime FLAG injection (k8s deployment)
if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then
    echo -n "$FLAG" > /var/www/.app_secret
    chmod 400 /var/www/.app_secret
    chown www-data:www-data /var/www/.app_secret
    unset FLAG
fi

exec apache2-foreground
