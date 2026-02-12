#!/bin/bash
set -e

# If FLAG is provided as runtime environment variable, update the config file
if [ -n "${FLAG}" ] && [ "${FLAG}" != "${FLAG_DEFAULT}" ]; then
    mkdir -p /var/solara/data/config
    echo -n "${FLAG}" > /var/solara/data/config/app.key
fi

# Unset FLAG from environment to prevent disclosure via /proc/self/environ
unset FLAG
unset FLAG_DEFAULT

# Ensure CDN cache directory has correct permissions
chmod -R 755 /var/www/solara/app/cdn_cache 2>/dev/null || true

# Start application server
cd /var/www/solara
exec python3 run.py
